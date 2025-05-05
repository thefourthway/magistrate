import psycopg2
from magistrate.main import _main, _create_argument_parser
from test.test_common import TEST_DATA_FOLDER
import os
import pytest

_directory = os.path.join(TEST_DATA_FOLDER, 'test_migrations_data', 'test_entrypoint')

@pytest.fixture(scope='function')
def postgres_environ(conn_string):

    os.environ['POSTGRES'] = conn_string

    yield conn_string

    del os.environ['POSTGRES']

def test_migration_up(conn_string, postgres_environ, db):
    args = [
        '--version',
        'latest',
        '--directory',
        _directory
    ]

    ap = _create_argument_parser()

    args = ap.parse_args(args)

    _main(args)

    with psycopg2.connect(conn_string) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT val, email FROM abc')

            values = cur.fetchall()

            assert values[0][0] == 22
            assert values[0][1] is None


def test_migration_down(conn_string, postgres_environ, db):
    args = [
        '--version',
        'latest',
        '--directory',
        _directory
    ]

    ap = _create_argument_parser()

    parsed = ap.parse_args(args)

    _main(parsed)

    with psycopg2.connect(conn_string) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT val, email FROM abc')

            values = cur.fetchall()

            assert values[0][0] == 22
            assert values[0][1] is None
    
    args = [
        '--version',
        '1',
        '--directory',
        _directory
    ]

    parsed = ap.parse_args(args)

    _main(parsed)

    with psycopg2.connect(conn_string) as conn:
        with conn.cursor() as cur:
            with pytest.raises(psycopg2.errors.UndefinedColumn):
                cur.execute('SELECT val, email FROM abc')
    
    args = [
        '--version',
        '0',
        '--directory',
        _directory
    ]

    parsed = ap.parse_args(args)

    _main(parsed)

    with psycopg2.connect(conn_string) as conn:
        with conn.cursor() as cur:
            with pytest.raises(psycopg2.errors.UndefinedTable):
                cur.execute('SELECT val, email FROM abc')
    