from magistrate.dbexc import MigrationFailed
from magistrate.parser import Migration
from magistrate.execution import HardcodedSource, MigrationParameters, VersionMigration, execute_migration
import psycopg2
import psycopg2.errors
import pytest

def test_simple_valid_up_migration(conn_string, db):
    migrations = [
        Migration(
            version=1,
            up_queries=[
                'CREATE TABLE abc (id serial primary key, val integer);',
                'INSERT INTO abc (val) VALUES (22);'
            ],
            down_queries=[
                'DROP TABLE abc;'
            ],
            backwards_compatible=True
        )
    ]

    params = MigrationParameters(
        connection_string=conn_string,
        migration_source=HardcodedSource(
            migrations=migrations
        ),
        migration_type=VersionMigration(target_version='latest')
    )
    
    new_version = execute_migration(params)

    assert new_version == 1

    with psycopg2.connect(conn_string) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT val FROM abc')

            values = cur.fetchall()

            assert values[0][0] == 22

def test_simple_valid_down_migration(conn_string, db):
    migrations = [
        Migration(
            version=1,
            up_queries=[
                'CREATE TABLE abc (id serial primary key, val integer);',
                'INSERT INTO abc (val) VALUES (22);'
            ],
            down_queries=[
                'DROP TABLE abc;'
            ],
            backwards_compatible=True
        ),
        Migration(
            version=2,
            up_queries=[
                'ALTER TABLE abc ADD COLUMN email TEXT'
            ],
            down_queries=[
                'ALTER TABLE abc DROP COLUMN email'
            ],
            backwards_compatible=True
        )
    ]

    params = MigrationParameters(
        connection_string=conn_string,
        migration_source=HardcodedSource(
            migrations=migrations
        ),
        migration_type=VersionMigration(target_version='latest')
    )
    
    new_version = execute_migration(params)

    assert new_version == 2

    with psycopg2.connect(conn_string) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT val, email FROM abc')

            values = cur.fetchall()

            assert values[0][0] == 22
            assert values[0][1] is None
    
    params.migration_type = VersionMigration(
        target_version=1
    )

    new_version = execute_migration(params)

    assert new_version == 1

    with psycopg2.connect(conn_string) as conn:
        with pytest.raises(psycopg2.errors.UndefinedColumn):

            with conn.cursor() as cur:
                cur.execute('SELECT val, email FROM abc')

    params.migration_type = VersionMigration(
        target_version=0
    )

    new_version = execute_migration(params)

    assert new_version == 0

    with psycopg2.connect(conn_string) as conn:
        with pytest.raises(psycopg2.errors.UndefinedTable):
            with conn.cursor() as cur:
                cur.execute('SELECT val FROM abc')
    
