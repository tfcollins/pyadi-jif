# from adijif.jesd import jesd
import numpy as np
from adijif.converters.converter import converter

# References
# https://ez.analog.com/wide-band-rf-transceivers/design-support-adrv9008-1-adrv9008-2-adrv9009/f/q-a/103757/adrv9009-clock-configuration/308013#308013


class adrv9009(converter):

    name = "ADRV9009"

    direct_clocking = False
    available_jesd_modes = ["jesd204b"]
    K_possible = [*np.arange(20, 256, 4)]
    L_possible = [1, 2, 4]
    M_possible = [1, 2, 4]
    N_possible = [12, 16, 24]
    Np_possible = [12, 16, 24]
    F_possible = [1, 2, 4, 8, 16]
    CS_possible = [0]
    CF_possible = [0]
    S_possible = [1]  # Not found in DS
    link_min = 3.6864e9
    link_max = 12.288e9

    max_rx_sample_clock = 250e6
    max_tx_sample_clock = 500e6
    max_obs_sample_clock = 500e6

    # Input clock requirements
    available_input_clock_dividers = [1 / 2, 1, 2, 4, 8, 16]
    input_clock_divider = 1

    device_clock_min = 10e6
    device_clock_max = 1e9

    """ Clocking
        ADRV9009 uses onboard PLLs to generate the JESD clocks

        Lane Rate = I/Q Sample Rate * M * Np * (10 / 8) / L
        Lane Rate = sample_clock * M * Np * (10 / 8) / L
    """
    max_input_clock = 4e9

    def get_required_clocks(self):
        """ Generate list of required clocks
            For ADRV9009 this will contain:
            [device clock requirement SOS, sysref requirement SOS]
        """
        possible_sysrefs = []
        for n in range(1, 20):
            r = self.multiframe_clock / (n * n)
            if r == int(r):
                possible_sysrefs.append(r)

        self.config = {"sysref": self.model.sos1(possible_sysrefs)}
        self.model.Obj(self.config["sysref"])

        possible_device_clocks = []
        for div in self.available_input_clock_dividers:
            dev_clock = self.sample_clock / div
            if self.device_clock_min <= dev_clock <= self.device_clock_max:
                possible_device_clocks.append(dev_clock)

        self.config["device_clock"] = self.model.sos1(possible_device_clocks)
        self.model.Obj(-1 * self.config["device_clock"])

        return [self.config["device_clock"], self.config["sysref"]]
        # return [possible_device_clocks[1], self.config["sysref"]]

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
