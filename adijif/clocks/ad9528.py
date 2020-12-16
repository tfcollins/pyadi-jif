import numpy as np
from adijif.clocks.clock import clock


class ad9528(clock):
    """ AD9528 Model """

    """ VCO divider """
    m1_available = [3, 4, 5]

    """ Output dividers """
    d_available = np.arange(1, 1024, 1, dtype=int)

    vco_min = 3450e6
    vco_max = 4025e6

    pfd_max = 275e6

    use_vcxo_double = False

    """ VCXO multiplier """
    n1_available = [16, 17, 20, 21, 22, 24, 25, 26, *range(28, 255)]  # VCO Cal divider
    n2_available = range(1, 257)
    a_available = range(0, 4)
    b_available = range(3, 64)
    # N = (PxB) + A, P=4, A==[0,1,2,3], B=[3..63]
    # See table 46 of DS for limits
    """ VCXO dividers """
    r1_available = range(1, 32)

    def __init__(self):
        pass

    def list_possible_references(self, divider_set):
        """ list_possible_references: Based on config list possible
            references that can be generated based on VCO and output
            dividers
        """
        # Check input
        ref = {
            "m1": 3,
            "n2": 2,
            "vco": 3000000000,
            "r1": 24,
            "required_output_divs": np.array([1.0]),
        }
        for key in ref:
            if key not in divider_set:
                raise Exception(
                    "Input must be of type dict with fields: " + str(ref.keys())
                )
        return [
            divider_set["vco"] / divider_set["m1"] / div for div in self.d_available
        ]

    def find_dividers(self, vcxo, required_output_rates, find=3):

        if self.use_vcxo_double:
            vcxo *= 2

        mod = np.gcd.reduce(np.array(required_output_rates, dtype=int))
        configs = []

        for r1 in self.r1_available:
            pfd = vcxo / r1
            if pfd > self.pfd_max:
                continue
            for m1 in self.m1_available:
                for n2 in self.n2_available:
                    # RECHECK THIS. NOT WELL DOCUMETNED
                    if n2 * m1 not in self.n1_available and not self.use_vcxo_double:
                        continue
                    if n2 * m1 * 2 not in self.n1_available:
                        continue
                    vco = pfd * m1 * n2
                    # Check bounds and integer
                    if (
                        vco > self.vco_min
                        and vco < self.vco_max
                        and (vco / m1) % mod == 0
                    ):
                        required_output_divs = (vco / m1) / required_output_rates
                        if np.all(np.in1d(required_output_divs, self.d_available)):
                            configs.append(
                                {
                                    "m1": m1,
                                    "vco": vco,
                                    "n2": n2,
                                    "r1": r1,
                                    "required_output_divs": required_output_divs,
                                }
                            )

        return configs
