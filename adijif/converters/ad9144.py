# from adijif.jesd import jesd
import numpy as np
from adijif.converters.converter import converter


class ad9144(converter):

    name = "AD9144"

    direct_clocking = True
    use_direct_clocking = True

    available_jesd_modes = ["jesd204b"]
    K_possible = [4, 8, 12, 16, 20, 24, 28, 32]
    L_possible = [1, 2, 4]
    M_possible = [1, 2, 4, 8]
    N_possible = [*range(7, 16)]
    Np_possible = [8, 16]
    F_possible = [1, 2, 4, 8, 16]
    CS_possible = [0, 1, 2, 3]
    CF_possible = [0]
    S_possible = [1]  # Not found in DS
    link_min = 3.125e9
    link_max = 12.5e9

    # Input clock requirements
    available_input_clock_dividers = [1, 2, 4, 8]
    input_clock_divider = 1
    available_datapath_interpolation = [1, 2, 4, 8]
    datapath_interpolation = 1

    # Internal limits
    pfd_min = 35e6
    pfd_max = 80e6

    config = {}  # type: ignore

    """ Clocking
        AD9144 has directly clocked DAC that have optional input dividers.
        The sample rate can be determined as follows:

        baseband_sample_rate = (input_clock / input_clock_divider) / datapath_decimation
    """
    max_input_clock = 4e9

    def _pll_config(self):

        dac_clk = self.datapath_interpolation * self.sample_clock
        self.config["dac_clk"] = self.model.Const(dac_clk)
        self.config["ref_div_factor"] = self.model.sos1([1, 2, 4, 8, 16])
        self.config["BCount"] = self.model.Var(integer=True, lb=6, ub=127)
        self.config["ref_clk"] = self.model.Var(integer=True, lb=35e6, ub=1e9)

        if dac_clk > 2800e6:
            raise Exception("DAC Clock too fast")
        elif dac_clk >= 1500e6:
            self.config["lo_div_mode_p2"] = self.model.Const(2 ** (1 + 1))
        elif dac_clk >= 720e6:
            self.config["lo_div_mode_p2"] = self.model.Const(2 ** (2 + 1))
        elif dac_clk >= 420e6:
            self.config["lo_div_mode_p2"] = self.model.Const(2 ** (3 + 1))
        else:
            raise Exception("DAC Clock too slow")

        self.config["vco"] = self.model.Intermediate(
            self.config["dac_clk"] * self.config["lo_div_mode_p2"]
        )

        self.model.Equation(
            [
                self.config["ref_div_factor"] * self.pfd_min < self.config["ref_clk"],
                self.config["ref_div_factor"] * self.pfd_max > self.config["ref_clk"],
                self.config["ref_clk"] * 2 * self.config["BCount"]
                == self.config["dac_clk"] * self.config["ref_div_factor"],
            ]
        )

        return self.config["ref_clk"]

    def get_required_clocks(self):
        """ Generate list required clocks
            For AD9144 this will contain [converter clock, sysref requirement SOS]
        """
        possible_sysrefs = []
        for n in range(1, 20):
            r = self.multiframe_clock / (n * n)
            if r == int(r) and r > 1e6:
                possible_sysrefs.append(r)
        self.config["sysref"] = self.model.sos1(possible_sysrefs)

        if self.use_direct_clocking:
            clk = self.sample_clock * self.datapath_interpolation
            # LaneRate = (20 × DataRate × M)/L
            assert self.bit_clock == (20 * self.sample_clock * self.M) / self.L
        else:
            # vco = dac_clk * 2^(LO_DIV_MODE + 1)
            # 6 GHz <= vco <= 12 GHz
            # BCount = floor( dac_clk/(2 * ref_clk/ref_div ) )
            # 5 <= BCount <= 127
            # ref_div = 2^ref_div_mode = 1,2,4,8,16
            clk = self._pll_config()

        print(self.config)

        self.model.Obj(self.config["sysref"])  # This breaks many searches

        return [clk, self.config["sysref"]]

    def device_clock_available(self):
        """ Generate list of possible device clocks """
        raise Exception("Not implemented")
        # aicd = sorted(self.available_input_clock_dividers)

        # dev_clocks = []
        # for div in aicd:
        #     in_clock = self.sample_clock * self.datapath_decimation * div
        #     if in_clock <= self.max_input_clock:
        #         dev_clocks.append(in_clock)
        # if not dev_clocks:
        #     raise Exception(
        #         "No device clocks possible in current config. Sample rate too high"
        #     )
        # return dev_clocks

    def device_clock_ranges(self):
        """ Generate min and max values for device clock """

        clks = self.device_clock_available()
        return np.min(clks), np.max(clks)

    def sysref_clock_ranges(self):
        """ sysref must be multiple of LMFC """
        lmfc = self.multiframe_clock
        return lmfc / 2048, lmfc / 2

    def sysref_met(self, sysref_clock, sample_clock):
        if sysref_clock % self.multiframe_clock != 0:
            raise Exception("SYSREF not a multiple of LMFC")
        if (self.multiframe_clock / sysref_clock) < 2 * self.input_clock_divider:
            raise Exception("SYSREF not a multiple of LMFC > 1")
