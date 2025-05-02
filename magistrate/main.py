import argparse

from magistrate.parser import MigrationDirection

def _create_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="GD Migration Tool")

    def _parse_migration_number(value):
        if value == "latest":
            return value
        try:
            return int(value)
        except ValueError:
            raise argparse.ArgumentTypeError("Version must be an integer or 'latest'")    
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--direction", "-d",
        type=MigrationDirection,
        choices=list(MigrationDirection),
        help="Direction of migration: up/down/latest"
    )

    group.add_argument(
        "--version", "-v",
        type=_parse_migration_number,
        help="Target version number"
    )
    parser.add_argument(
        "--migration-dir", "-m",
        required=False,
        help="Path to migration directory"
    )

    parser.add_argument(
        '--backup-dir', '-b',
        required=False,
        help='Path to backup directory'
    )

    return parser


def _main(args: argparse.Namespace):
    pass

if __name__ == '__main__':
    _parser = _create_argument_parser()
    args = _parser.parse_args()

    _main(args)
