from magistrate.dbexc import MigrationFailed
from magistrate.parser import Migration
from magistrate.execution import HardcodedSource, MigrationParameters, VersionMigration, execute_migration
import psycopg2

def test_simple_valid_migration(conn_string, db):
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

    try:
        execute_migration(params)
    except MigrationFailed as ex:
        cause = ex.__cause__
        assert False

    with psycopg2.connect(conn_string) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT val FROM abc')

            values = cur.fetchall()

            assert values[0][0] == 22
    