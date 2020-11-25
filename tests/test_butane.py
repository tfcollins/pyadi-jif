#!/usr/bin/env python

"""Tests for `butane` package."""

import pytest

# from click.testing import CliRunner

# from butane import butane
# from butane import cli
import adijif

# @pytest.fixture
# def response():
#     """Sample pytest fixture.

#     See more at: http://doc.pytest.org/en/latest/fixture.html
#     """
#     # import requests
#     # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


# def test_content(response):
#     """Sample pytest test function with the pytest fixture as an argument."""
#     # from bs4 import BeautifulSoup
#     # assert 'GitHub' in BeautifulSoup(response.content).title.string


# def test_command_line_interface():
#     """Test the CLI."""
#     runner = CliRunner()
#     result = runner.invoke(cli.main)
#     assert result.exit_code == 0
#     assert 'butane.cli.main' in result.output
#     help_result = runner.invoke(cli.main, ['--help'])
#     assert help_result.exit_code == 0
#     assert '--help  Show this message and exit.' in help_result.output

# def test_daq2_config():
#     # RX
#     j = butane.jesd()
#     j.L = 4
#     j.M = 2
#     j.S = 1
#     j.N = 16
#     j.Np = 16

#     print(j.conversion_clock)

def test_mxfe_config():
    # RX
    j = adijif.jesd()
    j.sample_clock = 250e6
    j.L = 4
    j.M = 8
    j.S = 1
    j.N = 16
    j.Np = 16
    j.K = 32

    assert j.bit_clock == 10000000000
    assert j.multiframe_clock == 7812500

def test_ad9680_config():
    # Full bandwidth example 1
    j = adijif.ad9680()
    j.sample_clock = 1e9
    j.L = 4
    j.M = 2
    j.N = 14
    j.Np = 16
    j.K = 32
    j.S = 1 # assumed

    assert j.F == 1
    assert j.bit_clock == 10e9
    # assert j.multiframe_clock == 7812500

def test_adrv9009_zcu102_config():

    s

