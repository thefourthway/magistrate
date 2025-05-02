import os

from magistrate.execution import DirectorySource
from test.test_common import TEST_DATA_FOLDER

_directory_source_folder = os.path.join(TEST_DATA_FOLDER, 'test_migrations_data/test_directory_select_migrations')

def test_directory_source_selection():
    ds = DirectorySource(
        directory=_directory_source_folder
    )

    current_version = 4
    target_version = 3

    selected = ds.select_migrations(current_version, target_version)
    assert len(selected) == 1
    assert selected[0].version == 4

    current_version = 3
    target_version = 4

    selected = ds.select_migrations(current_version, target_version)
    assert len(selected) == 1
    assert selected[0].version == 4

    current_version = 2
    target_version = 4

    selected = ds.select_migrations(current_version, target_version)

    assert len(selected) == 2
    assert selected[0].version == 3
    assert selected[1].version == 4

    current_version = 4
    target_version = 2

    selected = ds.select_migrations(current_version, target_version)
    
    assert len(selected) == 2
    assert selected[0].version == 4
    assert selected[1].version == 3
