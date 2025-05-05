import os
import shutil
import subprocess
import typing
import psycopg2

from magistrate.dbexc import IncompatibleVersions, MultipleVersionsFound, NoVersionsFound, VersionTableNotFound
from magistrate.exc import PGDumpError, PGDumpNotFound

if typing.TYPE_CHECKING:
    from magistrate.parser import Migration

_pg_dump_binary = shutil.which('pg_dump')

def backup_db(backup_filename: str, conn_string: str, *, pg_dump_binary_path: str | None = _pg_dump_binary):
    if pg_dump_binary_path is None:
        raise PGDumpNotFound(os.environ['PATH'])

    backup_filename = os.path.abspath(backup_filename)

    args = [
        'pg_dump',
        conn_string,
        '-f',
        backup_filename
    ]

    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            check=True
        )
        code = result.returncode
        err_output: str = ''
    except subprocess.CalledProcessError as e:
        code = e.returncode
        err_output = str(e.stderr)
    
    if code == 0 or code == 1:
        return
    
    raise PGDumpError(code, err_output)

_create_migrations_query = '''DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_catalog.pg_class WHERE relname = 'magistrate_migrations' AND relkind = 'r') THEN
        CREATE TABLE magistrate_migrations (
            id SERIAL PRIMARY KEY,
            version INTEGER
        );
        INSERT INTO magistrate_migrations (version) VALUES (0);
    END IF;
END
$$ LANGUAGE plpgsql
'''

def prepare_migration_table(conn_string: str):
    with psycopg2.connect(conn_string) as con:
        with con.cursor() as cur:
            cur.execute(_create_migrations_query)

def get_current_migration_version(conn_string: str):
    with psycopg2.connect(conn_string) as con:
        with con.cursor() as cur:
            try:
                cur.execute('SELECT version FROM magistrate_migrations')
            except psycopg2.errors.UndefinedTable:
                raise VersionTableNotFound()
            
            versions = cur.fetchall()

            if len(versions) == 0:
                raise NoVersionsFound()
            
            if len(versions) > 1:
                raise MultipleVersionsFound()
            
            ver = versions[0][0]
            return ver

def migrate_up(conn_string: str, migration: 'Migration'):
    current_version = get_current_migration_version(conn_string)

    if migration.version != current_version + 1:
        raise IncompatibleVersions(current_version, migration.version)
    
    with psycopg2.connect(conn_string) as conn:
        with conn.cursor() as cur:
            try:
                conn.autocommit = False

                for query in migration.up_queries:
                    cur.execute(query)

                cur.execute('UPDATE magistrate_migrations SET version = %s', (migration.version,))

                conn.commit()
            except Exception:
                conn.rollback()
                raise 

def migrate_down(conn_string: str, migration: 'Migration'):
    current_version = get_current_migration_version(conn_string)

    if migration.version != current_version - 1:
        raise IncompatibleVersions(current_version, migration.version)
    
    with psycopg2.connect(conn_string) as conn:
        with conn.cursor() as cur:
            try:
                conn.autocommit = False

                for query in migration.up_queries:
                    cur.execute(query)

                cur.execute('UPDATE magistrate_migrations SET version = %s', (migration.version,))

                conn.commit()
            except Exception:
                conn.rollback()
                raise 