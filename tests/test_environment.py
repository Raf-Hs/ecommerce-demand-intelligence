"""Smoke tests for the local development environment."""

import sys

import duckdb
import pandas
import pyarrow


def test_python_version():
    assert sys.version_info[:2] == (3, 11)


def test_core_imports():
    assert duckdb.__version__
    assert pandas.__version__
    assert pyarrow.__version__
