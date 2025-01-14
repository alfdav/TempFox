from setuptools import setup

# Metadata is now in pyproject.toml
setup(
    packages=['tempfox'],
    package_data={'': ['*']},
    include_package_data=True,
)
