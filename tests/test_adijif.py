#!/usr/bin/env python

"""Tests for `adijif` package."""

import adijif
import numpy as np
import pytest

# from adijif import adijif
from adijif import cli

# from click.testing import CliRunner


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


# def test_command_line_interface():
#     """Test the CLI."""
#     runner = CliRunner()
#     result = runner.invoke(cli.main)
#     assert result.exit_code == 0
#     assert "adijif.cli.main" in result.output
#     help_result = runner.invoke(cli.main, ["--help"])
#     assert help_result.exit_code == 0
#     assert "--help  Show this message and exit." in help_result.output


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

    ref = [
        {"m1": 3, "n2": 24, "vco": 3000000000.0, "r2": 1, "required_output_divs": 1.0},
        {"m1": 3, "n2": 48, "vco": 3000000000.0, "r2": 2, "required_output_divs": 1.0},
        {"m1": 3, "n2": 72, "vco": 3000000000.0, "r2": 3, "required_output_divs": 1.0},
        {"m1": 3, "n2": 96, "vco": 3000000000.0, "r2": 4, "required_output_divs": 1.0},
        {"m1": 3, "n2": 120, "vco": 3000000000.0, "r2": 5, "required_output_divs": 1.0},
        {"m1": 3, "n2": 144, "vco": 3000000000.0, "r2": 6, "required_output_divs": 1.0},
        {"m1": 3, "n2": 168, "vco": 3000000000.0, "r2": 7, "required_output_divs": 1.0},
        {"m1": 3, "n2": 192, "vco": 3000000000.0, "r2": 8, "required_output_divs": 1.0},
        {"m1": 3, "n2": 216, "vco": 3000000000.0, "r2": 9, "required_output_divs": 1.0},
        {
            "m1": 3,
            "n2": 240,
            "vco": 3000000000.0,
            "r2": 10,
            "required_output_divs": 1.0,
        },
    ]
    assert len(cfs) == 10
    assert cfs == ref


def test_ad9523_1_daq2_config_force_m2():
    # Full bandwidth example 1b
    clk = adijif.ad9523_1()
    rates = np.array([1e9, 3e9 / 1000 / 4])
    vcxo = 125000000
    cfs = clk.find_dividers(vcxo, rates)
    assert len(cfs) == 40
    ref = [
        {
            "m1": 3,
            "m2": 4,
            "n2": 24,
            "vco": 3000000000.0,
            "r2": 1,
            "required_output_divs": [1.0],
            "required_output_divs2": [1000.0],
        },
        {
            "m1": 3,
            "m2": 5,
            "n2": 24,
            "vco": 3000000000.0,
            "r2": 1,
            "required_output_divs": [1.0],
            "required_output_divs2": [800.0],
        },
        {
            "m1": 4,
            "m2": 3,
            "n2": 24,
            "vco": 3000000000.0,
            "r2": 1,
            "required_output_divs": [1000.0],
            "required_output_divs2": [1.0],
        },
        {
            "m1": 5,
            "m2": 3,
            "n2": 24,
            "vco": 3000000000.0,
            "r2": 1,
            "required_output_divs": [800.0],
            "required_output_divs2": [1.0],
        },
        {
            "m1": 3,
            "m2": 4,
            "n2": 48,
            "vco": 3000000000.0,
            "r2": 2,
            "required_output_divs": [1.0],
            "required_output_divs2": [1000.0],
        },
        {
            "m1": 3,
            "m2": 5,
            "n2": 48,
            "vco": 3000000000.0,
            "r2": 2,
            "required_output_divs": [1.0],
            "required_output_divs2": [800.0],
        },
        {
            "m1": 4,
            "m2": 3,
            "n2": 48,
            "vco": 3000000000.0,
            "r2": 2,
            "required_output_divs": [1000.0],
            "required_output_divs2": [1.0],
        },
        {
            "m1": 5,
            "m2": 3,
            "n2": 48,
            "vco": 3000000000.0,
            "r2": 2,
            "required_output_divs": [800.0],
            "required_output_divs2": [1.0],
        },
        {
            "m1": 3,
            "m2": 4,
            "n2": 72,
            "vco": 3000000000.0,
            "r2": 3,
            "required_output_divs": [1.0],
            "required_output_divs2": [1000.0],
        },
        {
            "m1": 3,
            "m2": 5,
            "n2": 72,
            "vco": 3000000000.0,
            "r2": 3,
            "required_output_divs": [1.0],
            "required_output_divs2": [800.0],
        },
        {
            "m1": 4,
            "m2": 3,
            "n2": 72,
            "vco": 3000000000.0,
            "r2": 3,
            "required_output_divs": [1000.0],
            "required_output_divs2": [1.0],
        },
        {
            "m1": 5,
            "m2": 3,
            "n2": 72,
            "vco": 3000000000.0,
            "r2": 3,
            "required_output_divs": [800.0],
            "required_output_divs2": [1.0],
        },
        {
            "m1": 3,
            "m2": 4,
            "n2": 96,
            "vco": 3000000000.0,
            "r2": 4,
            "required_output_divs": [1.0],
            "required_output_divs2": [1000.0],
        },
        {
            "m1": 3,
            "m2": 5,
            "n2": 96,
            "vco": 3000000000.0,
            "r2": 4,
            "required_output_divs": [1.0],
            "required_output_divs2": [800.0],
        },
        {
            "m1": 4,
            "m2": 3,
            "n2": 96,
            "vco": 3000000000.0,
            "r2": 4,
            "required_output_divs": [1000.0],
            "required_output_divs2": [1.0],
        },
        {
            "m1": 5,
            "m2": 3,
            "n2": 96,
            "vco": 3000000000.0,
            "r2": 4,
            "required_output_divs": [800.0],
            "required_output_divs2": [1.0],
        },
        {
            "m1": 3,
            "m2": 4,
            "n2": 120,
            "vco": 3000000000.0,
            "r2": 5,
            "required_output_divs": [1.0],
            "required_output_divs2": [1000.0],
        },
        {
            "m1": 3,
            "m2": 5,
            "n2": 120,
            "vco": 3000000000.0,
            "r2": 5,
            "required_output_divs": [1.0],
            "required_output_divs2": [800.0],
        },
        {
            "m1": 4,
            "m2": 3,
            "n2": 120,
            "vco": 3000000000.0,
            "r2": 5,
            "required_output_divs": [1000.0],
            "required_output_divs2": [1.0],
        },
        {
            "m1": 5,
            "m2": 3,
            "n2": 120,
            "vco": 3000000000.0,
            "r2": 5,
            "required_output_divs": [800.0],
            "required_output_divs2": [1.0],
        },
        {
            "m1": 3,
            "m2": 4,
            "n2": 144,
            "vco": 3000000000.0,
            "r2": 6,
            "required_output_divs": [1.0],
            "required_output_divs2": [1000.0],
        },
        {
            "m1": 3,
            "m2": 5,
            "n2": 144,
            "vco": 3000000000.0,
            "r2": 6,
            "required_output_divs": [1.0],
            "required_output_divs2": [800.0],
        },
        {
            "m1": 4,
            "m2": 3,
            "n2": 144,
            "vco": 3000000000.0,
            "r2": 6,
            "required_output_divs": [1000.0],
            "required_output_divs2": [1.0],
        },
        {
            "m1": 5,
            "m2": 3,
            "n2": 144,
            "vco": 3000000000.0,
            "r2": 6,
            "required_output_divs": [800.0],
            "required_output_divs2": [1.0],
        },
        {
            "m1": 3,
            "m2": 4,
            "n2": 168,
            "vco": 3000000000.0,
            "r2": 7,
            "required_output_divs": [1.0],
            "required_output_divs2": [1000.0],
        },
        {
            "m1": 3,
            "m2": 5,
            "n2": 168,
            "vco": 3000000000.0,
            "r2": 7,
            "required_output_divs": [1.0],
            "required_output_divs2": [800.0],
        },
        {
            "m1": 4,
            "m2": 3,
            "n2": 168,
            "vco": 3000000000.0,
            "r2": 7,
            "required_output_divs": [1000.0],
            "required_output_divs2": [1.0],
        },
        {
            "m1": 5,
            "m2": 3,
            "n2": 168,
            "vco": 3000000000.0,
            "r2": 7,
            "required_output_divs": [800.0],
            "required_output_divs2": [1.0],
        },
        {
            "m1": 3,
            "m2": 4,
            "n2": 192,
            "vco": 3000000000.0,
            "r2": 8,
            "required_output_divs": [1.0],
            "required_output_divs2": [1000.0],
        },
        {
            "m1": 3,
            "m2": 5,
            "n2": 192,
            "vco": 3000000000.0,
            "r2": 8,
            "required_output_divs": [1.0],
            "required_output_divs2": [800.0],
        },
        {
            "m1": 4,
            "m2": 3,
            "n2": 192,
            "vco": 3000000000.0,
            "r2": 8,
            "required_output_divs": [1000.0],
            "required_output_divs2": [1.0],
        },
        {
            "m1": 5,
            "m2": 3,
            "n2": 192,
            "vco": 3000000000.0,
            "r2": 8,
            "required_output_divs": [800.0],
            "required_output_divs2": [1.0],
        },
        {
            "m1": 3,
            "m2": 4,
            "n2": 216,
            "vco": 3000000000.0,
            "r2": 9,
            "required_output_divs": [1.0],
            "required_output_divs2": [1000.0],
        },
        {
            "m1": 3,
            "m2": 5,
            "n2": 216,
            "vco": 3000000000.0,
            "r2": 9,
            "required_output_divs": [1.0],
            "required_output_divs2": [800.0],
        },
        {
            "m1": 4,
            "m2": 3,
            "n2": 216,
            "vco": 3000000000.0,
            "r2": 9,
            "required_output_divs": [1000.0],
            "required_output_divs2": [1.0],
        },
        {
            "m1": 5,
            "m2": 3,
            "n2": 216,
            "vco": 3000000000.0,
            "r2": 9,
            "required_output_divs": [800.0],
            "required_output_divs2": [1.0],
        },
        {
            "m1": 3,
            "m2": 4,
            "n2": 240,
            "vco": 3000000000.0,
            "r2": 10,
            "required_output_divs": [1.0],
            "required_output_divs2": [1000.0],
        },
        {
            "m1": 3,
            "m2": 5,
            "n2": 240,
            "vco": 3000000000.0,
            "r2": 10,
            "required_output_divs": [1.0],
            "required_output_divs2": [800.0],
        },
        {
            "m1": 4,
            "m2": 3,
            "n2": 240,
            "vco": 3000000000.0,
            "r2": 10,
            "required_output_divs": [1000.0],
            "required_output_divs2": [1.0],
        },
        {
            "m1": 5,
            "m2": 3,
            "n2": 240,
            "vco": 3000000000.0,
            "r2": 10,
            "required_output_divs": [800.0],
            "required_output_divs2": [1.0],
        },
    ]
    assert cfs == ref


def test_daq2_fpga_qpll_rxtx_zc706_config():

    # Full bandwidth example 1b
    clk = adijif.ad9523_1()
    rates = 1e9
    vcxo = 125000000
    cfs = clk.find_dividers(vcxo, rates)
    assert len(cfs) == 10

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
    vcxo = 125000000

    sys = adijif.system("ad9680", "ad9523_1", "xilinx", vcxo)
    sys.converter.sample_clock = 1e9
    sys.converter.datapath_decimation = 1
    sys.converter.L = 4
    sys.converter.M = 2
    sys.converter.N = 14
    sys.converter.Np = 16
    sys.converter.K = 32
    sys.converter.F = 1

    sys.fpga.setup_by_dev_kit_name("zc706")

    clks = sys.determine_clocks()

    ref = [
        {
            "Converter": np.array(1000000000),
            "ClockChip": [
                {
                    "m1": 3,
                    "n2": 24,
                    "vco": 3000000000.0,
                    "r2": 1,
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
                },
                {
                    "m1": 3,
                    "n2": 48,
                    "vco": 3000000000.0,
                    "r2": 2,
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
                },
                {
                    "m1": 3,
                    "n2": 72,
                    "vco": 3000000000.0,
                    "r2": 3,
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
                },
                {
                    "m1": 3,
                    "n2": 96,
                    "vco": 3000000000.0,
                    "r2": 4,
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
                },
                {
                    "m1": 3,
                    "n2": 120,
                    "vco": 3000000000.0,
                    "r2": 5,
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
                },
                {
                    "m1": 3,
                    "n2": 144,
                    "vco": 3000000000.0,
                    "r2": 6,
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
                },
                {
                    "m1": 3,
                    "n2": 168,
                    "vco": 3000000000.0,
                    "r2": 7,
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
                },
                {
                    "m1": 3,
                    "n2": 192,
                    "vco": 3000000000.0,
                    "r2": 8,
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
                },
                {
                    "m1": 3,
                    "n2": 216,
                    "vco": 3000000000.0,
                    "r2": 9,
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
                },
                {
                    "m1": 3,
                    "n2": 240,
                    "vco": 3000000000.0,
                    "r2": 10,
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
                },
            ],
        }
    ]
    assert clks == ref


def test_adc_clk_solver():

    vcxo = 125000000
    sys = adijif.system("ad9680", "ad9523_1", "xilinx", vcxo)

    # Get Converter clocking requirements
    sys.converter.sample_clock = 1e9
    sys.converter.datapath_decimation = 1
    sys.converter.L = 4
    sys.converter.M = 2
    sys.converter.N = 14
    sys.converter.Np = 16
    sys.converter.K = 32
    sys.converter.F = 1

    cnv_clocks = sys.converter.get_required_clocks()

    sys.clock._update_model(vcxo, cnv_clocks)

    sys.model.options.SOLVER = 1  # APOPT solver
    sys.model.solve(disp=False)

    # for c in sys.clock.config:
    #     vs = sys.clock.config[c]
    #     for v in vs:
    #         if len(vs)>1:
    #             print(c,v[0])
    #         else:
    #             print(c,v)
    assert sys.clock.config["r2"].value[0] == 1
    assert sys.clock.config["m1"].value[0] == 3
    assert sys.clock.config["n2"].value[0] == 24
    assert sys.clock.config["out_dividers"][0][0] == 1
    assert sys.clock.config["out_dividers"][1][0] == 800


def test_fpga_solver():

    vcxo = 125000000
    sys = adijif.system("ad9680", "ad9523_1", "xilinx", vcxo)

    # Get Converter clocking requirements
    sys.converter.sample_clock = 1e9
    sys.converter.datapath_decimation = 1
    sys.converter.L = 4
    sys.converter.M = 2
    sys.converter.N = 14
    sys.converter.Np = 16
    sys.converter.K = 32
    sys.converter.F = 1

    cnv_config = type("AD9680", (), {})()
    cnv_config.bit_clock = 10e9

    sys.fpga.setup_by_dev_kit_name("zc706")
    required_clocks = sys.fpga._get_required_clocks_qpll(cnv_config)

    sys.clock._update_model(vcxo, [required_clocks])

    sys.model.options.SOLVER = 1  # APOPT solver
    sys.model.solve(disp=True)
    sys.model.options = [
        "minlp_maximum_iterations 1000",  # minlp iterations with integer solution
        "minlp_max_iter_with_int_sol 100",  # treat minlp as nlp
        "minlp_as_nlp 0",  # nlp sub-problem max iterations
        "nlp_maximum_iterations 5000",  # 1 = depth first, 2 = breadth first
        "minlp_branch_method 1",  # maximum deviation from whole number
        "minlp_integer_tol 0.05",  # covergence tolerance
        "minlp_gap_tol 0.01",
    ]
    # "fpga_pll_config": {
    #     "vco": 10000000000.0,
    #     "band": 1,
    #     "d": 1,
    #     "m": 1,
    #     "n": 20,
    #     "qty4_full_rate": 0,
    #     "type": "QPLL",
    # },
    clk_config = sys.clock.config
    print(clk_config)
    divs = sys.clock.config["out_dividers"]
    assert clk_config["n2"][0] == 25
    assert clk_config["r2"][0] == 1
    assert clk_config["m1"][0] == 5
    assert sys.fpga.config["fpga_ref"].value[0] == 620000000
    # for div in divs:
    #     assert div[0] in [1, 2, 1023]


def test_sys_solver():
    vcxo = 125000000

    sys = adijif.system("ad9680", "ad9523_1", "xilinx", vcxo)

    # Get Converter clocking requirements
    sys.converter.sample_clock = 1e9
    sys.converter.datapath_decimation = 1
    sys.converter.L = 4
    sys.converter.M = 2
    sys.converter.N = 14
    sys.converter.Np = 16
    sys.converter.K = 32
    sys.converter.F = 1

    cnv_clocks = sys.converter.get_required_clocks()

    # Get FPGA clocking requirements
    sys.fpga.setup_by_dev_kit_name("zc706")
    fpga_dev_clock = sys.fpga._get_required_clocks_qpll(sys.converter)

    # Collect all requirements
    sys.clock._update_model(vcxo, [fpga_dev_clock] + cnv_clocks)

    sys.model.options.SOLVER = 1  # APOPT solver
    # sys.model.solver_options = ['minlp_maximum_iterations 1000', \
    #                     # minlp iterations with integer solution
    #                     'minlp_max_iter_with_int_sol 100', \
    #                     # treat minlp as nlp
    #                     'minlp_as_nlp 0', \
    #                     # nlp sub-problem max iterations
    #                     'nlp_maximum_iterations 5000', \
    #                     # 1 = depth first, 2 = breadth first
    #                     'minlp_branch_method 1', \
    #                     # maximum deviation from whole number
    #                     'minlp_integer_tol 0.05', \
    #                     # covergence tolerance
    #                     'minlp_gap_tol 0.01']

    sys.model.solve(disp=False)

    clk_config = sys.clock.config
    print(clk_config)
    divs = sys.clock.config["out_dividers"]
    assert clk_config["n2"][0] == 24
    assert clk_config["r2"][0] == 1
    assert clk_config["m1"][0] == 3
    assert sys.fpga.config["fpga_ref"].value[0] == 500000000
    for div in divs:
        assert div[0] in [1, 2, 800]


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
