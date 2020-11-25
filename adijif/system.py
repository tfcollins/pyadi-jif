import numpy as np
import adijif


class system:

    def __init__(self, conv, clk, fpga, vcxo):

        assert isinstance(clk,adijif.clock), "clk input must be of type adijif.clock"
        assert isinstance(conv,adijif.jesd), "conv input must be of type adijif.converter"
        assert isinstance(fpga,adijif.fpga), "fpga input must be of type adijif.fpga"
        self.converter = conv
        self.clock = clk
        self.fpga = fpga
        self.vcxo = vcxo
        self.configs_to_find = 3

    def determine_clocks(self):
        # Extract dependent rates from converter
        rates = [self.converter.device_clock, self.converter.multiframe_clock]
        rates = np.array(rates, dtype=int)

        # Search across clock chip settings for supported modes
        clk_config = self.clock.find_dividers(self.vcxo, rates, find=self.configs_to_find)

        # Search FPGA settings



        return clk_config

