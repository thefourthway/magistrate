import argparse
import os
import sys
import typing

from magistrate.db import get_current_migration_version
from magistrate.execution import DirectorySource, MigrationParameters, VersionMigration, execute_migration

def _parse_version(value: str) -> int | typing.Literal['latest']:
    if value == "latest":
        return "latest"
    try:
        val = int(value)
        if val < 0:
            raise ValueError()
        
        return val
    except ValueError:
        raise argparse.ArgumentTypeError("Version must be a zero or positive integer or 'latest'")

def _create_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Magistrate migration tool")

    exclusive = parser.add_mutually_exclusive_group(required=True)

    exclusive.add_argument(
        "--get-version",
        action="store_true",
        help="Print current migration version"
    )

    exclusive.add_argument(
        "--version",
        type=_parse_version,
        help="Target version to migrate to (zero/positive integer or 'latest')"
    )

    parser.add_argument(
        "--directory",
        type=str,
        help="Path to migration files (required with --version)"
    )

    return parser

def _validate_args(parser: argparse.ArgumentParser, args: argparse.Namespace):
    if args.get_version and args.directory:
        parser.error('--get-version cannot be combined with --version or --directory')
    if (args.directory and not args.version) or (args.version and not args.directory):
        parser.error('--directory and --version must be specified together')

def _get_args(parser: argparse.ArgumentParser) -> argparse.Namespace:
    args = parser.parse_args()

    _validate_args(parser, args)

    return args

def _main(args: argparse.Namespace):
    try:
        conn_string = os.environ['POSTGRES']
    except KeyError:
        print('POSTGRES not found in os.environ, exiting')
        sys.exit(1)

    if args.get_version:
        current_version = get_current_migration_version(conn_string)
        print('Current version is', current_version)
        sys.exit(0)

    migration_directory = args.directory
    version: int | typing.Literal['latest'] = args.version

    migration_params = MigrationParameters(
        connection_string=conn_string,
        migration_source=DirectorySource(directory=migration_directory),
        migration_type=VersionMigration(
            target_version=version,
        )
    )

    new_version: int = execute_migration(migration_params)

    print('Database migrated. New version is', new_version)

if __name__ == '__main__':
    _parser = _create_argument_parser()
    args = _get_args(_parser)

    _main(args)
