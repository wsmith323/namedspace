__author__ = 'warren'

import doctest

import namedspace

def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(namedspace))
    return tests
