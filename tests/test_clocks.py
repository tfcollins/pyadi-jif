import adijif
import pytest
from gekko import GEKKO


def test_ad9523_1_daq2_validate():

    vcxo = 125000000
    n2 = 24

    clk = adijif.ad9523_1()

    # Check config valid
    clk.n2 = n2
    clk.use_vcxo_double = False

    output_clocks = [1e9, 500e6, 7.8125e6]
    clock_names = ["ADC", "FPGA", "SYSREF"]

    clk.set_requested_clocks(vcxo, output_clocks, clock_names)

    clk.solve()

    o = clk.get_config()

    # print(o)

    assert sorted(o["out_dividers"]) == [1, 2, 128]
    assert o["m1"] == 3
    assert o["m1"] in clk.m1_available
    assert o["n2"] == n2
    assert o["n2"] in clk.n2_available
    assert o["r2"] == 1
    assert o["r2"] in clk.r2_available


def test_ad9523_1_daq2_validate_fail():

    with pytest.raises(Exception, match=r"Solution Not Found"):
        vcxo = 125000000
        n2 = 12

        clk = adijif.ad9523_1()

        # Check config valid
        clk.n2 = n2
        # clk.r2 = 1
        clk.use_vcxo_double = False
        # clk.m = 3

        output_clocks = [1e9, 500e6, 7.8125e6]
        clock_names = ["ADC", "FPGA", "SYSREF"]

        clk.set_requested_clocks(vcxo, output_clocks, clock_names)

        clk.model.options.SOLVER = 1  # APOPT solver
        clk.model.solve(disp=False)

        o = clk.get_config()

        print(o)

        assert sorted(o["out_dividers"]) == [1, 2, 128]
        assert o["n2"] == n2


def test_ad9523_1_daq2_variable_vcxo_validate():

    vcxo = adijif.types.range(100000000, 126000000, 1000000, "vcxo")
    n2 = 24

    clk = adijif.ad9523_1()

    # Check config valid
    clk.n2 = n2
    clk.use_vcxo_double = False

    output_clocks = [1e9, 500e6, 7.8125e6]
    clock_names = ["ADC", "FPGA", "SYSREF"]

    clk.set_requested_clocks(vcxo, output_clocks, clock_names)

    clk.solve()

    o = clk.get_config()

    # print(o)

    assert sorted(o["out_dividers"]) == [1, 2, 128]
    assert o["m1"] == 3
    assert o["m1"] in clk.m1_available
    assert o["n2"] == n2
    assert o["n2"] in clk.n2_available
    assert o["r2"] == 1
    assert o["r2"] in clk.r2_available
    assert o["output_clocks"]["ADC"]["rate"] == 1e9
    assert o["vcxo"] == 125000000