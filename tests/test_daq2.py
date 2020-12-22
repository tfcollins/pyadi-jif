import adijif
import pytest


def print_sys(sys):
    print("----- Clock config:")
    for c in sys.clock.config:
        vs = sys.clock.config[c]
        if not isinstance(vs, list) and not isinstance(vs, dict):
            print(c, vs.value)
            continue
        for v in vs:
            if len(vs) > 1:
                print(c, v[0])
            else:
                print(c, v)

    print("----- FPGA config:")
    for c in sys.fpga.config:
        vs = sys.fpga.config[c]
        if not isinstance(vs, list) and not isinstance(vs, dict):
            print(c, vs.value)
            continue
        for v in vs:
            if len(vs) > 1:
                print(c, v[0])
            else:
                print(c, v)

    print("----- Converter config:")
    for c in sys.converter.config:
        vs = sys.converter.config[c]
        if not isinstance(vs, list) and not isinstance(vs, dict):
            print(c, vs.value)
            continue
        for v in vs:
            if len(vs) > 1:
                print(c, v[0])
            else:
                print(c, v)


def test_fpga_cpll_solver():

    vcxo = 125000000
    sys = adijif.system("ad9680", "hmc7044", "xilinx", vcxo)
    sys.fpga.setup_by_dev_kit_name("zc706")
    sys.fpga.force_cpll = 1

    sys.converter.sample_clock = 1e9 / 2
    sys.converter.datapath_decimation = 1
    sys.converter.L = 4
    sys.converter.M = 2
    sys.converter.N = 14
    sys.converter.Np = 16
    sys.converter.K = 32
    sys.converter.F = 1

    if 0:
        # cnv_config = type("AD9680", (), {})()
        # cnv_config.bit_clock = 10e9/2
        required_clocks = sys.fpga.get_required_clocks_qpll(sys.converter)
        sys.clock.set_requested_clocks(vcxo, [required_clocks])

        sys.model.options.SOLVER = 1  # APOPT solver
        sys.model.solve(disp=False)
    else:
        sys.solve()

    # print_sys(sys)


@pytest.mark.parametrize(
    "qpll, cpll, rate", [(0, 0, 1e9), (0, 1, 1e9 / 2), (1, 0, 1e9 / 2)]
)
@pytest.mark.parametrize("clock_chip", ["ad9523_1", "hmc7044", "ad9528"])
def test_ad9680_all_clk_chips_solver(qpll, cpll, rate, clock_chip):

    vcxo = 125000000

    sys = adijif.system("ad9680", clock_chip, "xilinx", vcxo)

    # Get Converter clocking requirements
    sys.converter.sample_clock = rate
    sys.converter.datapath_decimation = 1
    sys.converter.L = 4
    sys.converter.M = 2
    sys.converter.N = 14
    sys.converter.Np = 16
    sys.converter.K = 32
    sys.converter.F = 1

    sys.fpga.setup_by_dev_kit_name("zc706")
    sys.fpga.force_cpll = cpll
    sys.fpga.force_qpll = qpll

    sys.solve()

    if qpll:
        sys.fpga.config["qpll_0_cpll_1"] == 0
    elif cpll:
        sys.fpga.config["qpll_0_cpll_1"] == 1

    print_sys(sys)


def test_ad9144_solver():

    vcxo = 125000000
    sys = adijif.system("ad9144", "hmc7044", "xilinx", vcxo)
    sys.fpga.setup_by_dev_kit_name("zc706")
    # sys.fpga.force_cpll = 1

    sys.converter.sample_clock = 1e9
    # Mode 0
    sys.converter.datapath_decimation = 1
    sys.converter.L = 8
    sys.converter.M = 4
    sys.converter.N = 16
    sys.converter.Np = 16
    sys.converter.K = 32
    sys.converter.F = 1
    sys.converter.use_direct_clocking = False

    assert sys.converter.S == 1
    assert sys.converter.bit_clock == 10e9

    if 0:
        # cnv_config = type("AD9680", (), {})()
        # cnv_config.bit_clock = 10e9/2
        required_clocks = sys.fpga.get_required_clocks_qpll(sys.converter)
        sys.clock.set_requested_clocks(vcxo, [required_clocks])

        sys.model.options.SOLVER = 1  # APOPT solver
        sys.model.solve(disp=False)
    else:
        sys.solve()

    print_sys(sys)
