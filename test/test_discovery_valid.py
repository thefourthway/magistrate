import os

from magistrate.discovery import discover_migrations

_valid_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_discovery_data', 'valid'))

def test_discovery_valid():
    migrations = discover_migrations(_valid_folder)

    migrations = [
        (ver, os.path.basename(filename))
        for ver, filename in migrations
    ]

    migrations.sort(key=lambda x: x[0])

    assert migrations == [
        (1, '1.mig.sql'),
        (2, '2.mig.sql'),
        (3, '3.mig.sql'),
        (4, '4.mig.sql'),
        (5, '5.mig.sql')
    ]
