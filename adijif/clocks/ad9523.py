import numpy as np
from adijif.clocks.clock import clock


class ad9523_1(clock):
    """ AD9523-1 Model """

    """ VCO divider """
    m12_available = [3, 4, 5]

    """ Output dividers """
    d_available = np.arange(1, 1024, 1, dtype=int)

    """ Internal limits """
    vco_min = 2.94e9
    vco_max = 3.1e9
    pfd_max = 259e6

    """ Enable internal VCXO/PLL1 doubler """
    use_vcxo_double = False

    """ VCXO multiplier """
    n2_available = [12, 16, 17, 20, 21, 22, 24, 25, 26, *range(28, 255)]
    a_available = range(0, 4)
    b_available = range(3, 64)
    # N = (PxB) + A, P=4, A==[0,1,2,3], B=[3..63]
    # See table 46 of DS for limits

    """ VCXO dividers """
    r2_available = range(1, 32)

    def _setup_solver_constraints(self, vcxo):
        """ Apply constraints to solver model
        """
        self.config = {"r2": self.model.Var(integer=True, lb=1, ub=31, value=1)}
        self.config["m1"] = self.model.Var(integer=True, lb=3, ub=5)
        self.config["n2"] = self.model.sos1(self.n2_available)

        # PLL2 equations
        self.model.Equations(
            [
                vcxo / self.config["r2"] <= self.pfd_max,
                vcxo / self.config["r2"] * self.config["n2"] <= self.vco_max,
                vcxo / self.config["r2"] * self.config["n2"] >= self.vco_min,
            ]
        )
        # Minimization objective
        self.model.Obj(self.config["n2"])

    def set_requested_clocks(self, vcxo, out_freqs):
        """ set_requested_clocks: Define necessary clocks to be generated in model

            Parameters:
                vcxo:
                    VCXO frequency in hertz
                out_freqs:
                    list of required clocks to be output
        """
        # Setup clock chip internal constraints
        if self.use_vcxo_double:
            vcxo *= 2
        self._setup_solver_constraints(vcxo)

        # FIXME: ADD SPLIT m1 configuration support

        # Add requested clocks to output constraints
        self.config["out_dividers"] = []
        for out_freq in out_freqs:
            od = self.model.Var(integer=True, lb=1, ub=1023, value=1)
            # od = self.model.sos1([n*n for n in range(1,9)])
            self.model.Equations(
                [
                    vcxo
                    / self.config["r2"]
                    * self.config["n2"]
                    / self.config["m1"]
                    / od
                    == out_freq
                ]
            )
            self.config["out_dividers"].append(od)

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
                if pfb > self.pfd_max:
                    continue
                vco = pfb * n2
                if vco > self.vco_min and vco < self.vco_max:
                    for m1 in self.m12_available:
                        # print("vco",vco,mod,m1)
                        if (vco / m1) % mod == 0:
                            # See if we can use only m1 and not both m1+m2
                            rods = (vco / m1) / required_output_rates
                            if np.all(np.in1d(rods, self.d_available)):
                                configs.append(
                                    {
                                        "m1": m1,
                                        "n2": n2,
                                        "vco": vco,
                                        "r2": r2,
                                        "required_output_divs": rods,
                                    }
                                )
                            else:
                                # Try to use m2 as well to meet required out clocks
                                f1 = np.in1d(rods, self.d_available)
                                for m2 in self.m12_available:
                                    rods2 = (vco / m2) / required_output_rates
                                    f2 = np.in1d(rods2, self.d_available)
                                    if np.logical_or(f1, f2).all():
                                        configs.append(
                                            {
                                                "m1": m1,
                                                "m2": m2,
                                                "n2": n2,
                                                "vco": vco,
                                                "r2": r2,
                                                "required_output_divs": rods[
                                                    f1
                                                ].tolist(),
                                                "required_output_divs2": rods2[
                                                    f2
                                                ].tolist(),
                                            }
                                        )

        return configs
