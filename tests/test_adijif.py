#!/usr/bin/env python

"""Tests for `adijif` package."""

import adijif
import numpy as np
import pytest

# from adijif import adijif
from adijif import cli
from click.testing import CliRunner


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert "adijif.cli.main" in result.output
    help_result = runner.invoke(cli.main, ["--help"])
    assert help_result.exit_code == 0
    assert "--help  Show this message and exit." in help_result.output


# def test_mxfe_config():
#     # RX
#     j = adijif.jesd()
#     j.sample_clock = 250e6
#     j.L = 4
#     j.M = 8
#     j.S = 1
#     j.N = 16
#     j.Np = 16
#     j.K = 32

#     assert j.bit_clock == 10000000000
#     assert j.multiframe_clock == 7812500


def test_ad9680_config_ex1a():
    # Full bandwidth example 1a
    j = adijif.ad9680()
    j.sample_clock = 1e9
    j.L = 4
    j.M = 2
    j.N = 14
    j.Np = 16
    j.K = 32
    j.F = 1

    assert j.S == 1
    assert j.bit_clock == 10e9
    assert j.multiframe_clock == 7812500 * 4


def test_ad9680_config_ex1b():
    # Full bandwidth example 1b
    j = adijif.ad9680()
    j.sample_clock = 1e9
    j.L = 4
    j.M = 2
    j.N = 14
    j.Np = 16
    j.K = 32
    j.F = 2

    assert j.S == 2
    assert j.bit_clock == 10e9
    assert j.multiframe_clock == 7812500 * 2


def test_ad9680_config_ex2():
    # Full bandwidth example 1b
    j = adijif.ad9680()
    j.sample_clock = 1e9 / 16
    j.L = 1
    j.M = 8
    j.N = 14
    j.Np = 16
    j.K = 32
    j.F = 16

    assert j.S == 1  # assumed
    assert j.bit_clock == 10e9
    assert j.multiframe_clock == 7812500 / 4


def test_ad9523_1_daq2_config():
    # Full bandwidth example 1b
    clk = adijif.ad9523_1()
    rates = 1e9
    vcxo = 125000000
    cfs = clk.find_dividers(vcxo, rates)
    assert len(cfs) == 1
    assert cfs[0] == {"m1": 3, "vco": 3000000000, "r2": 24, "required_output_divs": 1}


def test_ad9523_1_daq2_config_force_m2():
    # Full bandwidth example 1b
    clk = adijif.ad9523_1()
    rates = np.array([1e9, 3e9 / 1000 / 4])
    vcxo = 125000000
    cfs = clk.find_dividers(vcxo, rates)
    assert len(cfs) == 4
    assert cfs == [
        {
            "m1": 3,
            "m2": 4,
            "vco": 3000000000,
            "r2": 24,
            "required_output_divs": [1.0],
            "required_output_divs2": [1000.0],
        },
        {
            "m1": 3,
            "m2": 5,
            "vco": 3000000000,
            "r2": 24,
            "required_output_divs": [1.0],
            "required_output_divs2": [800.0],
        },
        {
            "m1": 4,
            "m2": 3,
            "vco": 3000000000,
            "r2": 24,
            "required_output_divs": [1000.0],
            "required_output_divs2": [1.0],
        },
        {
            "m1": 5,
            "m2": 3,
            "vco": 3000000000,
            "r2": 24,
            "required_output_divs": [800.0],
            "required_output_divs2": [1.0],
        },
    ]


def test_daq2_fpga_qpll_rxtx_zc706_config():

    # Full bandwidth example 1b
    clk = adijif.ad9523_1()
    rates = 1e9
    vcxo = 125000000
    cfs = clk.find_dividers(vcxo, rates)
    assert len(cfs) == 1
    assert cfs[0] == {"m1": 3, "vco": 3000000000, "r2": 24, "required_output_divs": 1}

    adc = adijif.ad9680()
    adc.sample_clock = 1e9
    adc.datapath_decimation = 1
    adc.L = 4
    adc.M = 2
    adc.N = 14
    adc.Np = 16
    adc.K = 32
    adc.F = 1
    assert adc.S == 1
    assert adc.bit_clock == 10e9

    fpga = adijif.xilinx()
    fpga.transciever_type = "GTX2"
    fpga.fpga_family = "Zynq"
    fpga.fpga_package = "FF"
    fpga.speed_grade = -2

    refs = clk.list_possible_references(cfs[0])
    for ref in refs:
        try:
            info = fpga.determine_qpll(adc.bit_clock, ref)
            print("PASS", ref, info)
            break
        except:
            print("FAIL")
            continue
    ref = {
        "vco": 10000000000.0,
        "band": 1,
        "d": 1,
        "m": 1,
        "n": 20,
        "qty4_full_rate": 0,
        "type": "QPLL",
    }
    assert info == ref


def test_system_daq2_rx():
    adc = adijif.ad9680()
    adc.sample_clock = 1e9
    adc.datapath_decimation = 1
    adc.L = 4
    adc.M = 2
    adc.N = 14
    adc.Np = 16
    adc.K = 32
    adc.F = 1

    clk = adijif.ad9523_1()
    vcxo = 125000000

    fpga = adijif.xilinx()
    fpga.setup_by_dev_kit_name("zc706")

    sys = adijif.system(adc, clk, fpga, vcxo)
    clks = sys.determine_clocks()

    ref = {
        "Converter": np.array(1000000000),
        "ClockChip": [
            {
                "m1": 3,
                "vco": 3000000000,
                "r2": 24,
                "required_output_divs": 1.0,
                "fpga_pll_config": {
                    "vco": 10000000000.0,
                    "band": 1,
                    "d": 1,
                    "m": 1,
                    "n": 20,
                    "qty4_full_rate": 0,
                    "type": "QPLL",
                },
                "sysref_rate": 7812500.0,
            }
        ],
    }
    assert clks == [ref]


# def test_adrv9009_zcu102_config():

#     j = adijif.adrv9009()
#     j.sample_clock = 122880000
#     j.L = 4
#     j.M = 2
#     j.N = 14
#     j.Np = 16
#     j.K = 32
#     # j.S = 1 # assumed

#     fpga = adijif.xilinx()

# 	# XILINX_XCVR_TYPE_S7_GTX2 = 2,
# 	# XILINX_XCVR_TYPE_US_GTH3 = 5,
# 	# XILINX_XCVR_TYPE_US_GTH4 = 8,
# 	# XILINX_XCVR_TYPE_US_GTY4 = 9,
#     # This is a sythesis parameter defined in HDL not DT
#     fpga.transciever_type = 'GTH3'

#     # Defined in UG1182
#     fpga.fpga_family = 'Zynq'
#     fpga.fpga_package = 'FF'
#     fpga.speed_grade = -2
#     fpga.transceiver_voltage = 800 # FIXME

#     # adi,sys-clk-select
#     # Driver: adi,axi-adxcvr-1.0
#     #define GTH34_SYSCLK_CPLL		0
#     #define GTH34_SYSCLK_QPLL1		2
#     #define GTH34_SYSCLK_QPLL0		3
#     fpga.sys_clk_select = "GTH34_SYSCLK_CPLL"

#     # Lane rate
#     bit_clock = j.bit_clock
#     sysref_clock = 122800000

#     # Calc
#     vals1 = fpga.determine_cpll(bit_clock,sysref_clock)
#     vals2 = fpga.determine_qpll(bit_clock,sysref_clock)
