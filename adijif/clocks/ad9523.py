import numpy as np
from adijif.clocks.ad9523_1_bf import ad9523_1_bf


class ad9523_1(ad9523_1_bf):
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

    def get_config(self):
        config = {
            "m1": self.config["m1"].value[0],
            "n2": self.config["n2"].value[0],
            "r2": self.config["r2"].value[0],
            "out_dividers": [x.value[0] for x in self.config["out_dividers"]],
            "output_clocks": [],
        }

        clk = self.vcxo / config["r2"] * config["n2"] / config["m1"]
        for div in self.config["out_dividers"]:
            config["output_clocks"].append(clk / div.value[0])

        return config

    def _setup_solver_constraints(self, vcxo):
        """ Apply constraints to solver model
        """
        self.vcxo = vcxo
        self.config = {"r2": self.model.Var(integer=True, lb=1, ub=31, value=1)}
        self.config["m1"] = self.model.Var(integer=True, lb=3, ub=5, value=3)
        self.config["n2"] = self.model.sos1(self.n2_available)

        # PLL2 equations
        self.model.Equations(
            [
                vcxo / self.config["r2"] <= self.pfd_max,
                vcxo / self.config["r2"] * self.config["n2"] <= self.vco_max,
                vcxo / self.config["r2"] * self.config["n2"] >= self.vco_min,
            ]
        )
        # Objectives
        # self.model.Obj(self.config["n2"])

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
