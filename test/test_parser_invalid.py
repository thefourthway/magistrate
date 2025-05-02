import os
from io import StringIO
import typing
import pytest

from magistrate.exc import BackwardsIncompatibilityViolation, DisjointedSections, IncompleteQuery, InvalidMigrationVersion, ManualCommitDisabled, MissingSection, SectionNotSet, VersionCannotBeZero
from magistrate.parser import MigrationDirection, parse_migration

_invalid_migration_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 'test_parser_data', 'invalid'))


def _load_invalid_migration(name: str):
    with open(os.path.join(_invalid_migration_path, name), 'r') as f:
        return StringIO(f.read())


_invalid_parser_data: list[tuple[str, typing.Type[Exception], typing.Callable[[Exception], bool]]] = [
    # backwards compatibility tests
    (
        'backwards_incompatible_define_down.mig.sql',
        BackwardsIncompatibilityViolation,
        lambda ex: typing.cast(BackwardsIncompatibilityViolation,
                               ex).message == 'Migration declares itself backwards-incompatible, but defines a "down" section anyways'
    ),
    (
        'backwards_incompatible_multiple_declarations.mig.sql',
        BackwardsIncompatibilityViolation,
        lambda ex: typing.cast(BackwardsIncompatibilityViolation,
                               ex).message == 'Migration cannot declare backwards-incompatibility statements more than once'
    ),
    (
        'backwards_incompatible_late_declaration.mig.sql',
        BackwardsIncompatibilityViolation,
        lambda ex: typing.cast(BackwardsIncompatibilityViolation,
                               ex).message == 'Migration must declare itself backwards-incompatible before SQL statements are made'
    ),


    # query tests
    (
        'query_has_commit_statement.mig.sql',
        ManualCommitDisabled,
        lambda ex: True
    ),
    (
        'query_incomplete_query.mig.sql',
        IncompleteQuery,
        lambda ex: typing.cast(IncompleteQuery, ex).query == 'DROP TABLE \n'
    ),

    # section tests
    (
        'section_missing_down.mig.sql',
        MissingSection,
        lambda ex: typing.cast(
            MissingSection, ex).section == MigrationDirection.down
    ),
    (
        'section_missing_up_and_down.mig.sql',
        MissingSection,
        lambda ex: typing.cast(
            MissingSection, ex).section == MigrationDirection.up
    ),
    (
        'section_multiple_up_sections.mig.sql',
        DisjointedSections,
        lambda ex: typing.cast(
            DisjointedSections, ex).section == MigrationDirection.up
    ),
    (
        'section_section_not_set.mig.sql',
        SectionNotSet,
        lambda ex: True
    ),

    # version tests
    (
        'version_floating_point_version.mig.sql',
        InvalidMigrationVersion,
        lambda ex: typing.cast(InvalidMigrationVersion,
                               ex).line == '-- ver: 2.5'
    ),
    (
        'version_missing_version_line.mig.sql',
        InvalidMigrationVersion,
        lambda ex: typing.cast(InvalidMigrationVersion, ex).line == '-- up'
    ),
    (
        'version_missing_version.mig.sql',
        InvalidMigrationVersion,
        lambda ex: typing.cast(InvalidMigrationVersion, ex).line == '-- ver:'
    ),
    (
        'version_version_is_zero.mig.sql',
        VersionCannotBeZero,
        lambda ex: True
    )
]


@pytest.mark.parametrize('migration_filename,exception_type,exception_validator', _invalid_parser_data)
def test_invalid_parser_data(migration_filename, exception_type, exception_validator):
    migration_reader = _load_invalid_migration(migration_filename)

    with pytest.raises(exception_type) as exc_info:
        parse_migration(migration_reader)

    assert exception_validator(exc_info.value) is True
