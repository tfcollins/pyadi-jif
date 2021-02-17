"""AD9680 high speed ADC clocking model."""
from typing import Dict, List

from adijif.converters.ad9680_bf import ad9680_bf


class ad9680(ad9680_bf):
    """AD9680 high speed ADC model.

    This model supports direct clock configurations

    Clocking: AD9680 has directly clocked ADC that have optional input dividers.
    The sample rate can be determined as follows:

        baseband_sample_rate = (input_clock / input_clock_divider) / datapath_decimation
    """

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

    def get_required_clock_names(self) -> List[str]:
        """Get list of strings of names of requested clocks.

        This list of names is for the clocks defined by get_required_clocks

        Returns:
            List[str]: List of strings of clock names in order
        """
        return ["ad9680_adc_clock", "ad9680_sysref"]

    def get_required_clocks(self) -> Dict:
        """Generate list required clocks.

        For AD9680 this will contain [converter clock, sysref requirement SOS]

        Returns:
            Dict: Dictionary of solver variables, equations, and constants
        """
        # possible_sysrefs = []
        # for n in range(1, 10):
        #     r = self.multiframe_clock / (n * n)
        #     if r == int(r) and r > 1e6:
        #         possible_sysrefs.append(r)
        # self.config = {"sysref": self.model.sos1(possible_sysrefs)}

        self.config = {}
        self.config["lmfc_divisor_sysref"] = self.model.Var(
            integer=True, lb=1, ub=17, value=3  # default value must be odd
        )

        self.config["lmfc_divisor_sysref_squared"] = self.model.Intermediate(
            self.config["lmfc_divisor_sysref"] * self.config["lmfc_divisor_sysref"]
        )

        self.config["sysref"] = self.model.Intermediate(
            self.multiframe_clock / self.config["lmfc_divisor_sysref_squared"]
        )

        # Objectives
        # self.model.Obj(self.config["sysref"])  # This breaks many searches

        return [self.sample_clock, self.config["sysref"]]
