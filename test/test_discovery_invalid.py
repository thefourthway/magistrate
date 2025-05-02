import os
import typing
import pytest

from magistrate.discovery import discover_migrations
from magistrate.exc import DuplicateMigrationVersions, MissingMigrationVersion, MissingMigrationVersions

_invalid_discovery_base = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_discovery_data', 'invalid'))

_invalid_discovery_data: list[tuple[str, typing.Type[Exception], typing.Callable[[Exception], bool]]] = [
    (
        'migrations_missing_version_three',
        MissingMigrationVersion,
        lambda ex: typing.cast(MissingMigrationVersion, ex).known_versions == [1, 2, 4] and typing.cast(MissingMigrationVersion, ex).missing_version == 3
    ),
    (
        'migrations_missing_version_three_and_four',
        MissingMigrationVersions,
        lambda ex: typing.cast(MissingMigrationVersions, ex).known_versions == [1, 2, 5] and typing.cast(MissingMigrationVersions, ex).missing_versions == [3, 4]
    ),
    (
        'migrations_version_three_duplicated',
        DuplicateMigrationVersions,
        lambda ex: typing.cast(DuplicateMigrationVersions, ex).version == 3 and typing.cast(DuplicateMigrationVersions, ex).filenames[0].endswith('3_first.mig.sql') \
            and typing.cast(DuplicateMigrationVersions, ex).filenames[1].endswith('3_second.mig.sql')
    )
]

def discover_from(subfolder: str):
    return discover_migrations(os.path.join(_invalid_discovery_base, subfolder))


@pytest.mark.parametrize('test_folder,exception_type,exception_validator', _invalid_discovery_data)
def test_invalid_discovery_folder(test_folder, exception_type, exception_validator):
    with pytest.raises(exception_type) as exc_info:
        discover_from(test_folder)
    
    assert exception_validator(exc_info.value) is True
