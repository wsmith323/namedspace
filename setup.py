from setuptools import setup, find_packages

__version__ = "0.0.1"

def file_read(filename):
    with open(filename) as flo:
        return flo.read()

setup(
    name = "namedspace",
    version = __version__,
    packages = find_packages(),

    author = "Warren A. Smith",
    author_email = "warren@wandrsmith.net",
    description = file_read("README.md"),
    license = "PSF",
    keywords = "namedspace namespace",
    url = "https://github.com/wsmith323/namedspace",
    test_suite = "namedspace.tests",
)
