import numpy as np
from adijif.clocks.clock import clock


class ad9523_1(clock):
    """ AD9523-1 Model """

    """ VCO divider """
    m12_available = [3, 4, 5]
    """ Output dividers """
    d_available = np.arange(1, 1024, 1, dtype=int)

    vco_min = 2.94e9
    vco_max = 3.1e9

    pfb_max = 259e6

    use_vcxo_double = False

    """ VCXO multiplier """
    n2_available = [12, 16, 17, 20, 21, 22, 24, 25, 26, *range(28, 255)]
    a_available = range(0, 3)
    b_available = range(3, 63)
    # N = (PxB) + A, P=4, A==[0,1,2,3], B=[3..63]
    # See table 46 of DS for limits
    """ VCXO dividers """
    r2_available = range(1, 31)

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
            "vco": 3000000000,
            "r2": 24,
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

        # even =  np.arange(2, 4096, 2, dtype=int)
        # odivs = np.append([1, 3, 5], even)

        mod = np.gcd.reduce(np.array(required_output_rates, dtype=int))
        configs = []

        for n2 in self.n2_available:
            for r2 in self.r2_available:
                pfb = vcxo / r2
                if pfb > self.pfb_max:
                    continue
                vco = pfb * n2
                if vco > self.vco_min and vco < self.vco_max:
                    for m1 in self.m12_available:
                        # print("vco",vco,mod,m1)
                        if (vco / m1) % mod == 0:
                            # See if we can use only m1 and not both m1+m2
                            required_output_divs = (vco / m1) / required_output_rates
                            if np.all(np.in1d(required_output_divs, self.d_available)):
                                configs.append(
                                    {
                                        "m1": m1,
                                        "n2": n2,
                                        "vco": vco,
                                        "r2": r2,
                                        "required_output_divs": required_output_divs,
                                    }
                                )
                            else:
                                # Try to use m2 as well to meet required out clocks
                                f1 = np.in1d(required_output_divs, self.d_available)
                                for m2 in self.m12_available:
                                    required_output_divs2 = (
                                        vco / m2
                                    ) / required_output_rates
                                    f2 = np.in1d(
                                        required_output_divs2, self.d_available
                                    )
                                    if np.logical_or(f1, f2).all():
                                        configs.append(
                                            {
                                                "m1": m1,
                                                "m2": m2,
                                                "n2": n2,
                                                "vco": vco,
                                                "r2": r2,
                                                "required_output_divs": required_output_divs[
                                                    f1
                                                ].tolist(),
                                                "required_output_divs2": required_output_divs2[
                                                    f2
                                                ].tolist(),
                                            }
                                        )

        return configs
