# from adijif.jesd import jesd
import numpy as np
from adijif.converters.converter import converter


class ad9680(converter):

    name = "AD9680"

    direct_clocking = True
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
    available_datapath_decimation = [1, 2, 4, 8, 16]
    datapath_decimation = 1

    """ Clocking
        AD9680 has directly clocked ADCs that have optional input dividers.
        The sample rate can be determined as follows:

        baseband_sample_rate = (input_clock / input_clock_divider) / datapath_decimation
    """
    max_input_clock = 4e9

    def get_required_clocks(self):
        """ Generate list required clocks
            For AD9680 this will contain [converter clock, sysref requirement SOS]
        """
        possible_sysrefs = []
        for n in range(1, 20):
            r = self.multiframe_clock / (n * n)
            if r == int(r) and r > 1e6:
                possible_sysrefs.append(r)
        self.config = {"sysref": self.model.sos1(possible_sysrefs)}

        # Need to pick one of below
        self.config["sysref"].value = possible_sysrefs[-1]
        # self.model.Obj(self.config["sysref"])  # This breaks many searches

        return [self.sample_clock, self.config["sysref"]]

    def device_clock_available(self):
        """ Generate list of possible device clocks """
        aicd = sorted(self.available_input_clock_dividers)

        dev_clocks = []
        for div in aicd:
            in_clock = self.sample_clock * self.datapath_decimation * div
            if in_clock <= self.max_input_clock:
                dev_clocks.append(in_clock)
        if not dev_clocks:
            raise Exception(
                "No device clocks possible in current config. Sample rate too high"
            )
        return dev_clocks

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
