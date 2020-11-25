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

    j = adijif.adrv9009()
    j.sample_clock = 122880000
    j.L = 4
    j.M = 2
    j.N = 14
    j.Np = 16
    j.K = 32
    # j.S = 1 # assumed

    fpga = adijif.xilinx()

	# XILINX_XCVR_TYPE_S7_GTX2 = 2,
	# XILINX_XCVR_TYPE_US_GTH3 = 5,
	# XILINX_XCVR_TYPE_US_GTH4 = 8,
	# XILINX_XCVR_TYPE_US_GTY4 = 9,
    # This is a sythesis parameter defined in HDL not DT
    fpga.transciever_type = 'GTH3'

    # Defined in UG1182
    fpga.fpga_family = 'Zynq'
    fpga.fpga_package = 'FF'
    fpga.speed_grade = -2
    fpga.transceiver_voltage = 800 # FIXME

    # adi,sys-clk-select
    # Driver: adi,axi-adxcvr-1.0
    #define GTH34_SYSCLK_CPLL		0
    #define GTH34_SYSCLK_QPLL1		2
    #define GTH34_SYSCLK_QPLL0		3
    fpga.sys_clk_select = "GTH34_SYSCLK_CPLL"

    # Lane rate
    bit_clock = j.bit_clock
    sysref_clock = 122800000

    # Calc
    vals1 = fpga.determine_cpll(bit_clock,sysref_clock)
    vals2 = fpga.determine_qpll(bit_clock,sysref_clock)



