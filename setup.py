#setup.py 
#installs and runs tests for sqliteshelve
from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages
setup(
    name = "SQLiteShelve",
    version = "1.0",
    packages = find_packages(),
    scripts = ['shelve-tool'],
    author = "Michael Mabin",
    author_email = "d3vvnull@gmail.com",
    description = "A SQLite implementation of the Python Shelf",
    license = "PSF",
    keywords = "sqlite shelve database utility",
    url = "https://github.com/devnull255/sqlite-shelve"
)

