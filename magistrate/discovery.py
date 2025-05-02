import os

from magistrate.exc import DuplicateMigrationVersions, InvalidMigrationFile, InvalidMigrationVersion, MissingMigrationVersion, MissingMigrationVersions
from magistrate.parser import parse_migration_version


def discover_migrations(folder: str) -> list[tuple[int, str]]:
    filenames = [os.path.join(folder, x) for x in os.listdir(folder)]
    filenames = [os.path.abspath(x) for x in filenames]
    filenames = [x for x in filenames if x.endswith('.mig.sql')]

    migrations: dict[int, list[str]] = {}

    for filename in filenames:
        with open(filename, 'r') as f:
            version_line = f.readline().strip()

            try:
                version = parse_migration_version(version_line)
            except InvalidMigrationVersion as ex:
                raise InvalidMigrationFile(filename, str(ex)) from ex
            
            if version in migrations:
                # we will throw an error for these later
                migrations[version].append(filename)
            else:
                migrations[version] = [filename]

    for ver, fnames in migrations.items():
        if len(fnames) > 1:
            raise DuplicateMigrationVersions(ver, fnames)

    sorted_versions = sorted(list(migrations.keys()))

    sorted_result: list[tuple[int, str]] = []

    if len(sorted_versions) >= 1:
        if sorted_versions[0] != 1:
            raise MissingMigrationVersion(1, sorted_versions)
        
        if len(sorted_versions) > 1:
            for i in range(1, len(sorted_versions) - 1):
                version_diff = sorted_versions[i] - sorted_versions[i - 1]

                if version_diff == 1:
                    continue

                if version_diff == 2:
                    raise MissingMigrationVersion(sorted_versions[i] - 1, sorted_versions)
                
                if version_diff > 2:
                    missing_versions = list(range(sorted_versions[i - 1] + 1, sorted_versions[i]))
                    raise MissingMigrationVersions(missing_versions, sorted_versions)
        
        for ver in sorted_versions:
            sorted_result.append((ver, migrations[ver][0]))
    else:
        return []
    
    return sorted_result
