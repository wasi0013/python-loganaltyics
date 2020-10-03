#!/usr/bin/env python

"""Tests for `py_logan` package."""

import pytest

from click.testing import CliRunner
from py_logan import cli


def test_command_line_interface_with_no_arguments():
    """Command line invokation without the required arguments should fail with exit code 1"""
    runner = CliRunner()
    result = runner.invoke(cli.audit)
    assert result.exit_code == 1


