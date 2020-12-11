# from adijif.jesd import jesd
from adijif.converters.converter import converter


class ad9680(converter):

    name = "AD9680"

    direct_clocking = True
    available_jesd_modes = ["jesd204b"]
    K_possible = [4, 8, 12, 16, 20, 24, 28, 32]
    L_possible = [1, 2, 4]
    M_possible = [1, 2, 4, 8]
    N_possible = range(7, 16)
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
        AD9680 has directly clocked ADCs that have optional input dividers. The sample rate can be determined as follows:

        baseband_sample_rate = (input_clock / input_clock_divider) / datapath_decimation
    """
    max_input_clock = 4e9

    def __init__(self):
        pass

    def device_clock_ranges(self):
        """ Generate min and max values for device clock """

        aicd = sorted(self.available_input_clock_dividers)

        max_dc = False
        for div in aicd:
            in_clock = self.sample_clock * self.datapath_decimation * div
            print(in_clock)
            if in_clock <= self.max_input_clock:
                max_dc = in_clock
        if not max_dc:
            raise Exception("Device clock not possible. Sample rate too high")
        min_dc = self.sample_clock * self.datapath_decimation

        return min_dc, max_dc

    def sysref_clock_ranges(self):
        """ sysref must be multiple of LMFC """
        lmfc = self.multiframe_clock
        return lmfc / 2048, lmfc / 2

    def sysref_met(self, sysref_clock, sample_clock):
        if sysref_clock % self.multiframe_clock != 0:
            raise Exception("SYSREF not a multiple of LMFC")
        if (self.multiframe_clock / sysref_clock) < 2 * self.input_clock_divider:
            raise Exception("SYSREF not a multiple of LMFC > 1")
