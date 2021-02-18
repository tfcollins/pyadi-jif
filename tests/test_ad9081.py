import adijif

import pytest


def test_ad9081_rx_solver():
    vcxo = 100000000

    sys = adijif.system("ad9081_rx", "hmc7044", "xilinx", vcxo)
    sys.fpga.setup_by_dev_kit_name("zc706")
    sys.Debug_Solver = False
    # sys.fpga.request_device_clock = False

    sys.converter.use_direct_clocking = False

    # Get Converter clocking requirements
    sys.converter.sample_clock = 250e6
    sys.converter.datapath_decimation = 16
    sys.converter.L = 4
    sys.converter.M = 8
    sys.converter.N = 16
    sys.converter.Np = 16
    sys.converter.K = 32
    sys.converter.F = 4
    # sys.converter.S = 1

    # sys._try_fpga_configs()
    sys.solve()

    assert sys.fpga.configs[0]["qpll_0_cpll_1"].value[0] == 0  # QPLL


def test_ad9081_tx_solver():
    vcxo = 100000000

    sys = adijif.system("ad9081_tx", "hmc7044", "xilinx", vcxo)
    sys.fpga.setup_by_dev_kit_name("zc706")
    sys.Debug_Solver = False
    # sys.fpga.request_device_clock = False

    sys.converter.use_direct_clocking = False

    # Get Converter clocking requirements
    sys.converter.sample_clock = 250e6
    sys.converter.datapath_interpolation = 48
    sys.converter.L = 4
    sys.converter.M = 8
    sys.converter.N = 16
    sys.converter.Np = 16
    sys.converter.K = 32
    sys.converter.F = 4
    # sys.converter.S = 1

    # sys._try_fpga_configs()
    sys.solve()

    assert sys.fpga.configs[0]["qpll_0_cpll_1"].value[0] == 0  # QPLL