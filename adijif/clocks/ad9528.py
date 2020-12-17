import numpy as np
from adijif.clocks.clock import clock


class ad9528(clock):
    """ AD9528 Model """

    """ VCO divider """
    m1_available = [3, 4, 5]

    """ Output dividers """
    d_available = np.arange(1, 1024, 1, dtype=int)

    """ Internal limits """
    vco_min = 3450e6
    vco_max = 4025e6
    pfd_max = 275e6

    use_vcxo_double = False

    """ VCXO multiplier """
    n2_available = range(12, 255)
    # N = (PxB) + A, P=4, A==[0,1,2,3], B=[3..63]
    # See table 46 of DS for limits
    """ VCXO dividers """
    r1_available = range(1, 32)

    def _setup_solver_constraints(self, vcxo):
        """ Apply constraints to solver model
        """
        self.config = {"r1": self.model.Var(integer=True, lb=1, ub=31, value=1)}
        self.config["m1"] = self.model.Var(integer=True, lb=3, ub=5)
        self.config["n2"] = self.model.Var(integer=True, lb=12, ub=255)

        # PLL2 equations
        self.model.Equations(
            [
                vcxo / self.config["r1"] <= self.pfd_max,
                vcxo / self.config["r1"] * self.config["m1"] * self.config["n2"]
                <= self.vco_max,
                vcxo / self.config["r1"] * self.config["m1"] * self.config["n2"]
                >= self.vco_min,
            ]
        )
        # Minimization objective
        self.model.Obj(self.config["n2"] * self.config["m1"])

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

        # Add requested clocks to output constraints
        self.config["out_dividers"] = []
        for out_freq in out_freqs:
            od = self.model.Var(integer=True, lb=1, ub=256, value=1)
            # od = self.model.sos1([n*n for n in range(1,9)])
            self.model.Equations(
                [vcxo / self.config["r1"] * self.config["n2"] / od == out_freq]
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
