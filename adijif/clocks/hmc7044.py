import numpy as np
from adijif.clocks.hmc7044_bf import hmc7044_bf


class hmc7044(hmc7044_bf):

    r2_divider_min = 1
    r2_divider_max = 4095

    n2_divider_min = 8
    n2_divider_max = 65535

    """ Internal limits """
    vco_min = 2150e6
    vco_max = 3550e6
    pfd_max = 250e6
    vcxo_min = 10e6
    vcxo_max = 500e6

    """ Output dividers """
    d_available = [1, 3, 5, *np.arange(2, 4095, 2, dtype=int)]

    use_vcxo_double = True

    def _setup_solver_constraints(self, vcxo):
        """ Apply constraints to solver model
        """
        self.config = {"r2": self.model.Var(integer=True, lb=1, ub=4095, value=1)}
        self.config["n2"] = self.model.Var(
            integer=True, lb=8, ub=4095
        )  # FIXME: CHECK UB

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
        # self.model.Obj(-1 * vcxo / self.config["r2"])

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
        assert self.vcxo_min <= vcxo <= self.vcxo_max, "VCXO out of range"
        self._setup_solver_constraints(vcxo)

        # Add requested clocks to output constraints
        self.config["out_dividers"] = []
        for out_freq in out_freqs:
            even = self.model.Var(integer=True, lb=1, ub=4094 / 2)

            # odd = self.model.sos1([1, 3, 5])
            odd_i = self.model.Var(integer=True, lb=0, ub=2)
            odd = self.model.Intermediate(1 + odd_i * 2)

            eo = self.model.Var(integer=True, lb=0, ub=1)
            od = self.model.Intermediate(eo * odd + (1 - eo) * even * 2)

            self.model.Equations(
                [vcxo / self.config["r2"] * self.config["n2"] / od == out_freq]
            )
            self.config["out_dividers"].append(od)

            # Objectives
            # self.model.Obj(-1*eo) # Favor even dividers
