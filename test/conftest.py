import psycopg2
import pytest
from psycopg2 import sql
import os

@pytest.fixture(scope='function')
def conn_string():
    return os.environ['POSTGRES']

def _clear_database(conn_string):
    with psycopg2.connect(conn_string) as conn:
        with conn.cursor() as cur:
            # Drop tables
            cur.execute("""
                SELECT tablename FROM pg_tables
                WHERE schemaname = 'public';
            """)
            tables = cur.fetchall()
            for (table,) in tables:
                cur.execute(sql.SQL("DROP TABLE IF EXISTS {} CASCADE").format(sql.Identifier(table)))

            # Drop enum types
            cur.execute("""
                SELECT t.typname FROM pg_type t
                JOIN pg_namespace n ON n.oid = t.typnamespace
                WHERE t.typtype = 'e' AND n.nspname = 'public';
            """)
            types = cur.fetchall()
            for (typ,) in types:
                cur.execute(sql.SQL("DROP TYPE IF EXISTS {} CASCADE").format(sql.Identifier(typ)))

        conn.commit()

@pytest.fixture(scope="function")
def db(conn_string):
    _clear_database(conn_string)
    yield None
    _clear_database(conn_string)

