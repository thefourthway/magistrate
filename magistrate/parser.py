
import enum
import re
import pydantic
from magistrate.exc import BackwardsIncompatibilityViolation, DisjointedSections, IncompleteQuery, InvalidMigrationVersion, ManualCommitDisabled, MissingSection, SectionNotSet
from typing import Protocol

class MigrationDirection(enum.Enum):
    up = "up"
    down = "down"

    def __str__(self):
        return self.value

class _StringReader(Protocol):
    def read(self, __size: int = ...) -> str: ...
    def seek(self, __offset: int, __whence: int = ...) -> int: ...
    def readline(self, __size: int = ...) -> str: ...
    def tell(self) -> int: ...

class Migration(pydantic.BaseModel):
    version: int
    up_queries: list[str]
    down_queries: list[str]

    backwards_compatible: bool

def parse_migration_version(line: str) -> int:
    line = line.strip()

    ver_match = re.search(r'^--\s*ver:\s*([0-9]+)\s*$', line)

    if not ver_match:
        raise InvalidMigrationVersion(line)
    
    return int(ver_match.group(1))

def parse_migration_direction(line: str) -> MigrationDirection | None:
    line = line.strip()

    direction_match = re.search(r'^--\s*(up|down)\s*$', line)

    if not direction_match:
        return None
    
    return MigrationDirection(direction_match.group(1))

def parse_is_backwards_compatible(line: str) -> bool | None:
    line = line.strip()

    backcompat_match = re.search('^--\s*backwards_compatible:\s*(true|false)\s*$', line)

    if backcompat_match:
        return backcompat_match.group(1) == 'true'
    
    return None

def is_query_end(line: str) -> bool:
    line = line.strip()

    return line.endswith(';')

def has_commit_statement(query: str) -> bool:
    query = query.strip()

    commit_match = re.search(r'\s*commit\s*;', query, re.IGNORECASE | re.MULTILINE)
    return commit_match is not None

def parse_migration(fd: _StringReader) -> Migration:
    version_line = fd.readline()

    version = parse_migration_version(version_line)

    queries: dict[MigrationDirection, list[str]] = {
        MigrationDirection.up: [],
        MigrationDirection.down: []
    }

    back_compatible: bool | None = None

    accum: list[str] = []
    current_direction: MigrationDirection | None = None

    while (line := fd.readline()) != '':
        if (dir := parse_migration_direction(line)) is not None:
            if len(queries[dir]) > 0:
                raise DisjointedSections(dir)
            
            if dir == MigrationDirection.down and back_compatible is False:
                raise BackwardsIncompatibilityViolation('Migration declares itself backwards-incompatible, but defines a "down" section anyways')
            
            current_direction = dir
        elif (bc := parse_is_backwards_compatible(line)) is not None:
            if back_compatible is not None:
                raise BackwardsIncompatibilityViolation('Migration cannot declare backwards-incompatibility statements more than once')
            
            if current_direction is not None:
                raise BackwardsIncompatibilityViolation('Migration must declare itself backwards-incompatible before SQL statements are made')
            
            back_compatible = bc
        else:
            if current_direction is None:
                if line.strip() == '':
                    continue
                
                raise SectionNotSet()
            
            accum.append(line)

            if is_query_end(line):
                query = ''.join(accum)

                if has_commit_statement(query):
                    raise ManualCommitDisabled()

                queries[current_direction].append(query)
                accum = []
    
    if len(accum) > 0:
        raise IncompleteQuery(''.join(accum))
    
    if len(queries[MigrationDirection.up]) == 0:
        raise MissingSection(MigrationDirection.up)
    
    if len(queries[MigrationDirection.down]) == 0 and back_compatible in {None, True}:
        raise MissingSection(MigrationDirection.down)
    
    return Migration(
        version=version,
        up_queries=queries[MigrationDirection.up],
        down_queries=queries[MigrationDirection.down],
        backwards_compatible=True if back_compatible is None else back_compatible
    )
