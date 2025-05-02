from magistrate.exc import MigrationError


class DBError(MigrationError):
    pass

class VersionTableNotFound(DBError):
    pass

class NoVersionsFound(DBError):
    pass

class MultipleVersionsFound(DBError):
    pass

class IncompatibleVersions(DBError):
    def __init__(self, current: int, migration: int):
        self.current_version: int = current
        self.migration_version: int = migration
    
    def __repr__(self):
        return f'IncompatibleVersions({self.current_version}, {self.migration_version})'
    
    def __str__(self):
        return f'Current version {self.current_version} cannot be bumped to {self.migration_version}'

class CurrentVersionTooHigh(DBError):
    def __init__(self, current: int, highest: int):
        self.current_version: int = current
        self.highest_version: int = highest
    
    def __repr__(self):
        return f'CurrentVersionTooHigh({self.current_version}, {self.highest_version})'
    
    def __str__(self):
        return f'Current version {self.current_version} is higher than highest known migration at {self.highest_version}'

class TargetVersionTooHigh(DBError):
    def __init__(self, target: int, highest: int):
        self.target_version: int = target
        self.highest_version: int = highest

    def __repr__(self):
        return f'TargetVersionTooHigh({self.target_version}, {self.highest_version})'
    
    def __str__(self):
        return f'Target version {self.target_version} is higher than the highest known migration at {self.highest_version}'

class DowngradeIncompatible(DBError):
    def __init__(self, current: int, downgrade_incompatible: int, target: int):
        self.current_version: int = current
        self.downgrade_incompatible_version: int = downgrade_incompatible
        self.target_version: int = target
    
    def __repr__(self):
        return f'CannotDowngrade({self.current_version}, {self.downgrade_incompatible_version}, {self.target_version})'
    
    def __str__(self):
        return f'version {self.downgrade_incompatible_version} between current version {self.current_version} and target version {self.target_version} is backwards-incompatible'

class TargetBelowZero(DBError):
    def __repr__(self):
        return 'TargetBelowZero()'
    
    def __str__(self):
        return f'Target version is below zero and therefore impossible'
    
class MigrationFailed(DBError):
    def __init__(self, begin: int, failed: int, target: int, end: int):
        self.version_begin: int = begin
        self.version_failed: int = failed
        self.version_target: int = target
        self.version_end: int = end
    
    def __repr__(self):
        return f'MigrationFailed({self.version_begin}, {self.version_failed}, {self.version_target}, {self.version_end})'
    
    def __str__(self):
        return f'Migration failed. Migration began at {self.version_begin} with target version {self.version_target}. Migration failed at {self.version_failed}. Database state left at version {self.version_end}'
