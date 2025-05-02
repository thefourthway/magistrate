from magistrate.execution import HardcodedSource
from magistrate.parser import Migration


def test_hardcoded_source_selection():
    hs = HardcodedSource(
        migrations=[
            Migration(
                version=1,
                up_queries=[],
                down_queries=[],
                backwards_compatible=True
            ),
            Migration(
                version=2,
                up_queries=[],
                down_queries=[],
                backwards_compatible=True
            ),
            Migration(
                version=3,
                up_queries=[],
                down_queries=[],
                backwards_compatible=True
            ),
            Migration(
                version=4,
                up_queries=[],
                down_queries=[],
                backwards_compatible=True
            )
        ]
    )

    current_version = 4
    target_version = 3

    selected = hs.select_migrations(current_version, target_version)
    assert len(selected) == 1
    assert selected[0].version == 4

    current_version = 3
    target_version = 4

    selected = hs.select_migrations(current_version, target_version)
    assert len(selected) == 1
    assert selected[0].version == 4

    current_version = 2
    target_version = 4

    selected = hs.select_migrations(current_version, target_version)

    assert len(selected) == 2
    assert selected[0].version == 3
    assert selected[1].version == 4

    current_version = 4
    target_version = 2

    selected = hs.select_migrations(current_version, target_version)
    
    assert len(selected) == 2
    assert selected[0].version == 4
    assert selected[1].version == 3
