import pydantic

from magistrate.db import migrate_down, migrate_up, prepare_migration_table, get_current_migration_version
from magistrate.dbexc import DowngradeIncompatible, CurrentVersionTooHigh, MigrationFailed, TargetBelowZero, TargetVersionTooHigh
from magistrate.discovery import discover_migrations
from magistrate.parser import MigrationDirection, parse_migration
import typing

if typing.TYPE_CHECKING:
    from magistrate.parser import Migration

class VersionMigration(pydantic.BaseModel):
    target_version: int | typing.Literal['latest']

    @pydantic.model_validator(mode='after')
    def _validate_version_migration(self) -> 'VersionMigration':
        if self.target_version != 'latest' and self.target_version < 0:
            raise ValueError('Target version cannot be below zero')
        
        return self

class DirectionMigration(pydantic.BaseModel):
    direction: MigrationDirection

class MigrationParameters(pydantic.BaseModel):
    connection_string: str
    direction: MigrationDirection
    migration_directory: str
    backup_directory: str | None

    migration_type: VersionMigration | DirectionMigration

def _execute_migration_list(params: MigrationParameters, current_version: int, target_version: int, parsed_migrations: list['Migration']) -> int:
    living_db_version: int = current_version

    if target_version < current_version:
        # first check if any are backwards-incompatible BEFORE making any changes
        for mig in parsed_migrations:
            if not mig.backwards_compatible:
                raise DowngradeIncompatible(current_version, mig.version, target_version)
        
        for mig in parsed_migrations:
            try:
                migrate_down(params.connection_string, mig)
            except Exception as ex:
                raise MigrationFailed(current_version, mig.version, target_version, living_db_version) from ex
            
            living_db_version = mig.version - 1
    else:
        for mig in parsed_migrations:
            try:
                migrate_up(params.connection_string, mig)
            except Exception as ex:
                raise MigrationFailed(current_version, mig.version, target_version, living_db_version) from ex

            living_db_version = mig.version

    return living_db_version

def _execute_target_migration(params: MigrationParameters, current_version: int, target_version: int, highest_version: int, migrations: list[tuple[int, str]]) -> int:
    migrations_between: list[tuple[int, str]] = []

    if target_version > current_version:
        migrations_between = migrations[current_version:target_version]
    elif target_version < current_version:
        migrations_between = migrations_between[target_version:current_version][::-1]

    if len(migrations_between) == 0:
        return current_version
    
    parsed_migrations: list['Migration'] = []

    for _, filename in migrations_between:
        with open(filename, 'r') as f:
            parsed_migrations.append(parse_migration(f))
    
    expected_version: int = _execute_migration_list(params, current_version, target_version, parsed_migrations)

    new_current_version = get_current_migration_version(params.connection_string)

    assert new_current_version == expected_version

    return current_version
    
def _execute_version_migration(params: MigrationParameters, migration_type: VersionMigration, current_version: int, highest_version: int, migrations: list[tuple[int, str]]) -> int:
    target_version: int = -1

    if migration_type.target_version == 'latest':
        target_version = highest_version
    else:
        target_version = typing.cast(int, migration_type.target_version)

    if target_version == current_version:
        return current_version

    return _execute_target_migration(params, current_version, target_version, highest_version, migrations)

def execute_migration(params: MigrationParameters) -> int:
    prepare_migration_table(params.connection_string)
    current_version = get_current_migration_version(params.connection_string)
    
    migrations = discover_migrations(params.migration_directory)

    if len(migrations) == 0:
        return current_version
    
    highest_version = migrations[-1][0]

    if current_version > highest_version:
        raise CurrentVersionTooHigh(current_version, highest_version)
    
    if current_version == highest_version:
        return current_version

    if isinstance(params.migration_type, VersionMigration):
        if params.migration_type.target_version != 'latest' and params.migration_type.target_version > highest_version:
            raise TargetVersionTooHigh(params.migration_type.target_version, highest_version)
        
        return _execute_version_migration(params, typing.cast(VersionMigration, params.migration_type), current_version, highest_version, migrations)
    elif isinstance(params.migration_type, DirectionMigration):
        if params.migration_type.direction == MigrationDirection.up:
            target_version = current_version + 1
        elif params.migration_type == MigrationDirection.down:
            target_version = current_version - 1
        else:
            return current_version
        
        if target_version < 0:
            raise TargetBelowZero()

        return _execute_target_migration(params, current_version, target_version, highest_version, migrations)
    
    return current_version
    