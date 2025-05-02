import pydantic

from magistrate.db import migrate_down, migrate_up, prepare_migration_table, get_current_migration_version
from magistrate.dbexc import DowngradeIncompatible, CurrentVersionTooHigh, MigrationFailed, TargetBelowZero, TargetVersionTooHigh
from magistrate.discovery import discover_migrations
from magistrate.parser import MigrationDirection, parse_migration, Migration
import typing

class VersionMigration(pydantic.BaseModel):
    target_version: int | typing.Literal['latest']

    @pydantic.model_validator(mode='after')
    def _validate_version_migration(self) -> 'VersionMigration':
        if self.target_version != 'latest' and self.target_version < 0:
            raise ValueError('Target version cannot be below zero')
        
        return self

class DirectionMigration(pydantic.BaseModel):
    direction: MigrationDirection

class DirectorySource(pydantic.BaseModel):
    directory: str

    def select_migrations(self, current_version: int, target_version: int) -> list['Migration']:
        migration_files = discover_migrations(self.directory)

        migrations: list[Migration] = []

        selected: list[str] = []

        if current_version > target_version:
            tmp = migration_files[target_version:current_version][::-1]
            selected = [x[1] for x in tmp]
        elif current_version < target_version:
            tmp = migration_files[current_version:target_version]
            selected = [x[1] for x in tmp]
        
        for s in selected:
            with open(s, 'r') as f:
                migrations.append(parse_migration(f))

        return migrations

class HardcodedSource(pydantic.BaseModel):
    migrations: list[Migration]

    @pydantic.model_validator(mode='after')
    def _auto_sort_migrations(self):
        self.migrations.sort(key=lambda mig: mig.version)
        return self
    
    def select_migrations(self, current_version: int, target_version: int) -> list['Migration']:
        if current_version > target_version:
            return self.migrations[target_version:current_version][::-1]
        elif current_version < target_version:
            return self.migrations[current_version:target_version]
        
        return []

class MigrationParameters(pydantic.BaseModel):
    connection_string: str

    migration_source: DirectorySource | HardcodedSource
    migration_type: VersionMigration | DirectionMigration

    backup_directory: str | None = None

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

def _execute_target_migration(params: MigrationParameters, current_version: int, target_version: int) -> int:
    migrations = params.migration_source.select_migrations(current_version, target_version)

    if len(migrations) == 0:
        return current_version
    
    _execute_migration_list(params, current_version, target_version, migrations)

    new_current_version = get_current_migration_version(params.connection_string)

    return new_current_version
    
def _execute_version_migration(params: MigrationParameters, migration_type: VersionMigration, current_version: int, highest_version: int) -> int:
    target_version: int = -1

    if migration_type.target_version == 'latest':
        target_version = highest_version
    else:
        target_version = typing.cast(int, migration_type.target_version)

    if target_version == current_version:
        return current_version

    return _execute_target_migration(params, current_version, target_version)

def execute_migration(params: MigrationParameters) -> int:
    prepare_migration_table(params.connection_string)
    current_version = get_current_migration_version(params.connection_string)

    if isinstance(params.migration_source, DirectorySource):
        dsrc = typing.cast(DirectorySource, params.migration_source)
        migrations = discover_migrations(dsrc.directory)

        if len(migrations) == 0:
            return current_version
    
        highest_version = migrations[-1][0]
    elif isinstance(params.migration_source, HardcodedSource):
        hsrc = typing.cast(HardcodedSource, params.migration_source)

        if len(hsrc.migrations) == 0:
            return current_version
        
        highest_version = hsrc.migrations[-1].version
    else:
        return current_version

    if current_version > highest_version:
        raise CurrentVersionTooHigh(current_version, highest_version)
    
    if current_version == highest_version:
        return current_version

    if isinstance(params.migration_type, VersionMigration):
        if params.migration_type.target_version != 'latest' and params.migration_type.target_version > highest_version:
            raise TargetVersionTooHigh(params.migration_type.target_version, highest_version)
        
        return _execute_version_migration(params, typing.cast(VersionMigration, params.migration_type), current_version, highest_version)
    elif isinstance(params.migration_type, DirectionMigration):
        if params.migration_type.direction == MigrationDirection.up:
            target_version = current_version + 1
        elif params.migration_type == MigrationDirection.down:
            target_version = current_version - 1
        else:
            return current_version
        
        if target_version < 0:
            raise TargetBelowZero()
        
        if target_version > highest_version:
            raise TargetVersionTooHigh(target_version, highest_version)

        return _execute_target_migration(params, current_version, target_version)
    
    return current_version
    