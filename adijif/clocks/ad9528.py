import numpy as np
from adijif.clocks.ad9528_bf import ad9528_bf


class ad9528(ad9528_bf):
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
        self.config["m1"] = self.model.Var(integer=True, lb=3, ub=5, value=3)
        self.config["n2"] = self.model.Var(integer=True, lb=12, ub=255, value=12)

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
        # self.model.Obj(self.config["n2"] * self.config["m1"])

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
