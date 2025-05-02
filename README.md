# magistrate

Magistrate is a Python library for migrating PostgreSQL databases.

It is intended to be usable both programatically and via the command line.

Sample run in code:

```python
from magistrate.execution import MigrationParameters as MigrationParams, VersionMigration, DirectionMigration, \
 DirectorySource, HardcodedSource, execute_migration
from magistrate.parser import Migration, MigrationDirection
from magistrate.dbexc import DBError

# Migration from a directory of .mig.sql files to the latest version
params = MigrationParams(
    connection_string='postgresql://user:password@127.0.0.1/database',
    migration_source=DirectorySource(directory='/path/to/migration_files'),
    migration_type=VersionMigration(target_version='latest')
)

# Migration from a directory of .mig.sql files to bump or lower the version by 1
params = MigrationParams(
    connection_string='postgresql://user:password@127.0.0.1/database',
    migration_source=DirectorySource(directory='/path/to/migration_files'),
    migration_type=DirectionMigration(direction=MigrationDirection.up)
)

# Migration from a set of hardcoded Migration objects to a specific version
params = MigrationParams(
    connection_string='postgresql://user:password@127.0.0.1/database',
    migration_source=HardcodedSource(
        migrations=[
            Migration(
                version=1,
                up_queries=[
                    'CREATE TABLE abc (id serial primary key, version int);'
                ],
                down_queries=[
                    'DROP TABLE abc;'
                ],
                backwards_compatible=True
            ),
            Migration(
                version=2,
                up_queries=[
                    'ALTER TABLE abc ADD COLUMN new_col INTEGER;'
                ],
                down_queries=[
                    'ALTER TABLE abc DROP COLUMN new_col;'
                ]
            ),
            Migration(
                version=3,
                ...
            ),
            Migration(
                version=4,
                ...
            )
        ]
    ),
    migration_type=VersionMigration(target_version=3)
)

# And now, to execute the migration:

try:
    new_version: int = execute_migration(params)
    print('Database is now on version', new_version)
except DBError as ex: # specialize this to get more detailed error info
    ...
```

Sample run from the command line:

```bash
export POSTGRES='postgresql://user:pwd@localhost/db'

python -m magistrate.main --directory /path/to/migration_files --version latest
python -m magistrate.main --directory /path/to/migration_files --version 3
python -m magistrate.main --get-version

Database is currently migrated to version 2. Latest version is 4.
```

## .mig.sql

### Format
Migration files should always end in `.mig.sql`. Aside from the file extension, the files can by named anything - meaning that file naming is separate from versioning. This is to allow more flexibility in describing what each migration does, but it may be convenient for you to include something like `YYYY_MM_DD_` as a prefix before your description.

Migrations have a simple, but strict text format for defining your database changes.

Here is an example of a `.mig.sql` file:

```sql
-- ver: 1
-- up

CREATE TABLE abc (
    id serial primary key,
    value integer
);

CREATE TYPE status AS ENUM ('pending', 'approved', 'rejected');

-- down

DROP TYPE status;
DROP TABLE abc;
```

The very first line of a `.mig.sql` file must always define the version as an integer.

`-- ver: 1`

To define queries to run when installing this version, we define the `up` section like so:

`-- up`

To define queries to run when uninstalling this version, we define the `down` section like so:

`-- down`

Every query must end with a semicolon `;` or it will be considered incomplete and throw an error.

### Schema Backwards Compatibility
You may mark a migration version as being backwards-incompatible by adding this line before the `up` or `down` sections are defined:

`-- backwards_compatible: false`

An example of a non-backwards-compatible migration can be seen below:

```sql
-- ver: 2
-- backwards_compatible: false
-- up

UPDATE abc SET value = value + floor(random() * 100 + 1)::int;
```

## Database changes

magistrate needs a table in your database to track the version.

It will create a table called `magistrate_migrations`, in which there will be a row defining the version your database is currently migrated to.

DO NOT TOUCH THIS TABLE AT ALL.

## Automatic Backup

To be continued
