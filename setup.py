from setuptools import setup, find_packages

setup(
    name="magistrate",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "pydantic",
        "psycopg2-binary"
    ],
    entry_points={
        "console_scripts": [
            "magistrate = magistrate.main:_main_no_args"
        ]
    },
    python_requires=">=3.11",
)
