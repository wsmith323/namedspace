
import os

from setuptools import setup, find_packages

__version__ = "1.0.1"

def file_read(filename):
    filepath = os.path.join(os.path.dirname(__file__), filename)
    with open(filepath) as flo:
        return flo.read()

setup(
    name = "namedspace",
    version = __version__,
    packages = find_packages(),
    install_requires = ["frozendict"],
    author = "Warren A. Smith",
    author_email = "warren@wandrsmith.net",
    description = "Namespace class factory.",
    long_description = file_read("README.md"),
    license = "PSF",
    keywords = "namedspace namespace",
    url = "https://github.com/wsmith323/namedspace",
    test_suite = "tests",
)
