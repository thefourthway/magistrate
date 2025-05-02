from setuptools import setup, find_packages

setup(
    name="magistrate",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic",
        "psycopg2-binary"
    ],
    entry_points={
        "console_scripts": [
            "magistrate = magistrate.main:main"
        ]
    },
    python_requires=">=3.11",
)
