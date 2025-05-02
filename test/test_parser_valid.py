from io import StringIO
import pytest
import os
from typing import Type, Optional

from magistrate.parser import parse_migration

_valid_migration_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', 'test_parser_data', 'valid'))

def _load_valid_migration(name: str):
    with open(os.path.join(_valid_migration_path, name), 'r') as f:
        return StringIO(f.read())

_valid_parser_data: list[tuple[str, int, bool, list[str], list[str]]] = [
    (
        'ver_1_explicit_back_compatible_table_abc_type_status.mig.sql',
        1,
        True,
        [
'''CREATE TABLE abc(
    id BIGSERIAL PRIMARY KEY,
    version INTEGER
);''',
        'CREATE TYPE status (\'on\', \'off\', \'pending\');'
        ],
        [
            'DROP TYPE status;',
            'DROP TABLE abc;'
        ]
    ),
    (
        'ver_2_implicit_back_compatible_table_abc_type_status.mig.sql',
        2,
        True,
        [
'''CREATE TABLE abc(
    id BIGSERIAL PRIMARY KEY,
    version INTEGER
);''',
        'CREATE TYPE status (\'on\', \'off\', \'pending\');'
        ],
        [
            'DROP TYPE status;',
            'DROP TABLE abc;'
        ]
    ),
    (
        'ver_1_explicit_back_compatible_table_abc_type_status_down_first.mig.sql',
        1,
        True,
        [
'''CREATE TABLE abc(
    id BIGSERIAL PRIMARY KEY,
    version INTEGER
);''',
        'CREATE TYPE status (\'on\', \'off\', \'pending\');'
        ],
        [
            'DROP TYPE status;',
            'DROP TABLE abc;'
        ]
    ),
    (
        'ver_3_explicit_back_compatible_newline_up_newline_down.mig.sql',
        3,
        True,
        [
'''CREATE TABLE abc(
    id BIGSERIAL PRIMARY KEY,
    version INTEGER
);''',
        'CREATE TYPE status (\'on\', \'off\', \'pending\');'
        ],
        [
            'DROP TYPE status;',
            'DROP TABLE abc;'
        ]
    ),
    (
        'ver_1_back_incompatible_no_down_section.mig.sql',
        1,
        False,
        [
'''CREATE TABLE abc(
    id BIGSERIAL PRIMARY KEY,
    version INTEGER
);''',
        'CREATE TYPE status (\'on\', \'off\', \'pending\');'
        ],
        [],
    )
]

@pytest.mark.parametrize('migration_filename,version,backwards_compatible,up_queries,down_queries', _valid_parser_data)
def test_valid_parser_data(migration_filename, version, backwards_compatible, up_queries, down_queries):
    migration_reader = _load_valid_migration(migration_filename)
    parsed = parse_migration(migration_reader)

    assert parsed.version == version
    assert parsed.backwards_compatible == backwards_compatible

    cleaned_up = [x.strip() for x in parsed.up_queries]
    cleaned_down = [x.strip() for x in parsed.down_queries]

    assert cleaned_up == up_queries
    assert cleaned_down == down_queries
