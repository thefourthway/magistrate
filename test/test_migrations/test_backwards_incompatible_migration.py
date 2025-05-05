

from magistrate.dbexc import DowngradeIncompatible
from magistrate.execution import HardcodedSource, MigrationParameters, VersionMigration, execute_migration
from magistrate.parser import Migration
import psycopg2
import pytest
import typing

def test_backwards_incompatible_migration(conn_string, db):
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
                'UPDATE abc SET val = val + floor(random() * 100 + 1)::int;'
            ],
            down_queries=[],
            backwards_compatible=False
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
            cur.execute('SELECT val FROM abc')

            value = cur.fetchall()[0][0]

            assert value != 22
            assert value < 123
    
    params.migration_type = VersionMigration(target_version=1)

    with pytest.raises(DowngradeIncompatible) as exc_info:
        execute_migration(params)

    err = typing.cast(DowngradeIncompatible, exc_info.value)

    assert err.current_version == 2
    assert err.downgrade_incompatible_version == 2
    assert err.target_version == 1

    