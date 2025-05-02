import typing
import os

if typing.TYPE_CHECKING:
    from magistrate.parser import MigrationDirection

class MigrationError(Exception):
    pass

class InvalidMigrationVersion(MigrationError):
    def __init__(self, line: str):
        self.line: str = line
    
    def __repr__(self):
        return f'InvalidMigrationVersion({repr(self.line)})'
    
    def __str__(self):
        return f'Invalid migration version - "{self.line}" - Format is "-- ver: 1"'

class SectionNotSet(MigrationError):
    def __repr__(self):
        return 'SectionNotSet()'
    
    def __str__(self):
        return 'Section was not set before queries began'

class MissingSection(MigrationError):
    def __init__(self, section: 'MigrationDirection'):
        self.section: 'MigrationDirection' = section

    def __repr__(self):
        return f'MissingSection({repr(self.section)})'
    
    def __str__(self):
        return f'Migration was missing section: {str(self.section)}'

class DisjointedSections(MigrationError):
    def __init__(self, section: 'MigrationDirection'):
        self.section: 'MigrationDirection' = section
    
    def __repr__(self):
        return f'DisjointedSections({self.section})'
    
    def __str__(self):
        return f'Section {self.section} was found multiple times in the migration'

class IncompleteQuery(MigrationError):
    def __init__(self, query: str):
        self.query: str = query
    
    def __repr__(self):
        return f'IncompleteQuery({repr(self.query)})'
    
    def __str__(self):
        return f'Query in migration was not terminated with a semicolon: {repr(self.query)}'

class ManualCommitDisabled(MigrationError):
    def __repr__(self):
        return f'ManualCommitDisabled()'
    
    def __str__(self):
        return f'Migrations must not use the COMMIT statement themselves'

class BackwardsIncompatibilityViolation(MigrationError):
    def __init__(self, message: str):
        self.message: str = message

    def __repr__(self):
        return f'BackwardsIncompatibilityViolation({repr(self.message)})'
    
    def __str__(self):
        return f'Migration violates backwards incompatibility rules: {self.message}'
    
# All errors involving farming out to binaries should be placed after this line

class PGDumpNotFound(MigrationError):
    def __init__(self, path: str):
        self.path: str = path
    
    def __repr__(self):
        return f'PGDumpNotFound({repr(self.path)})'

    def __str__(self):
        return f'pg_dump executable not found in PATH: {self.path}'

class PGDumpError(MigrationError):
    def __init__(self, code: int, stderr_str: str):
        self.code: int = code
        self.stderr_str: str = stderr_str
    
    def __repr__(self):
        return f'PGDumpError({repr(self.stderr_str)})'
    
    def __str__(self):
        return f'pg_dump returned error code {self.code} - stderr: {self.stderr_str}'
    
# All errors involving specific files should be placed after this line

class InvalidMigrationFile(MigrationError):
    def __init__(self, filename: str, message: str):
        self.filename: str = filename
        self.message: str = message

    def __repr__(self):
        return f'InvalidMigrationFile({repr(self.filename)}, {repr(self.message)})'
    
    def __str__(self):
        return f'Invalid migration file: {self.filename}: {self.message}'

class MissingMigrationVersion(MigrationError):
    def __init__(self, missing_version: int, known_versions: list[int]):
        self.missing_version: int = missing_version
        self.known_versions: list[int] = known_versions
    
    def __repr__(self):
        return f'MissingMigrationVersion({self.missing_version}, {repr(self.known_versions)})'
    
    def __str__(self):
        return f'Migration version {self.missing_version} was not found amongst known versions {repr(self.known_versions)}'

class MissingMigrationVersions(MigrationError):
    def __init__(self, missing_versions: list[int], known_versions: list[int]):
        self.missing_versions: list[int] = missing_versions
        self.known_versions: list[int] = known_versions
    
    def __repr__(self):
        return f'MissingMigrationVersion({repr(self.missing_versions)}, {repr(self.known_versions)})'
    
    def __str__(self):
        s_missing = ', '.join(str(x) for x in self.missing_versions)
        s_known = ', '.join(str(x) for x in self.known_versions)

        return f'Migration versions {s_missing} were not found amongst known versions {s_known}'

class DuplicateMigrationVersions(MigrationError):
    def __init__(self, version: int, filenames: list[str]):
        self.version = version
        self.filenames = filenames

    def __repr__(self):
        return f'DuplicateMigrationVersions({repr(self.version)}, {repr(self.filenames)})'
    
    def __str__(self):
        nice_filenames = [os.path.basename(fname) for fname in self.filenames]
        return f'Duplicate migration version {self.version} found in the following files: {repr(nice_filenames)}'
