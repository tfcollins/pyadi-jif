import numpy as np
from adijif.clocks.hmc7044_bf import hmc7044_bf


class hmc7044(hmc7044_bf):

    # Ranges
    # r2_divider_min = 1
    # r2_divider_max = 4095
    r2_available = [*range(1, 4095 + 1)]
    # n2_divider_min = 8
    # n2_divider_max = 65535
    n2_available = [*range(1, 65535 + 1)]

    """ Output dividers """
    d_available = [1, 3, 5, *np.arange(2, 4095, 2, dtype=int)]
    # When pulse generation is required (like for sysref) divder range
    # is limited
    d_syspulse_available = [*np.arange(32, 4095, 2, dtype=int)]

    # Defaults
    _d = [1, 3, 5, *np.arange(2, 4095, 2, dtype=int)]
    _n2 = [*range(1, 65535 + 1)]
    _r2 = [*range(1, 4095 + 1)]

    # Limits
    """ Internal limits """
    vco_min = 2150e6
    vco_max = 3550e6
    pfd_max = 250e6
    vcxo_min = 10e6
    vcxo_max = 500e6

    use_vcxo_double = True

    # State management
    _clk_names = -1

    @property
    def d(self):
        """ d: Output dividers """
        return self._d

    @d.setter
    def d(self, value):
        self._check_in_range(value, self.d_available, "d")
        self._d = value

    @property
    def n2(self):
        """ n2: VCO feedback divider """
        return self._m2

    @n2.setter
    def n2(self, value):
        self._check_in_range(value, self.n2_available, "n2")
        self._m2 = value

    @property
    def r2(self):
        """ r2: VCXO input dividers """
        return self._r2

    @r2.setter
    def r2(self, value):
        self._check_in_range(value, self.r2_available, "r2")
        self._r2 = value

    def get_config(self):

        if not self._clk_names:
            raise Exception("set_requested_clocks must be called before get_config")

        config = {
            "r2": self.config["r2"].value[0],
            "n2": self.config["n2"].value[0],
            "out_dividers": [x.value[0] for x in self.config["out_dividers"]],
            "output_clocks": [],
        }

        clk = self.vcxo / config["r2"] * config["n2"]

        output_cfg = {}
        for i, div in enumerate(self.config["out_dividers"]):
            rate = clk / div.value[0]
            output_cfg[self._clk_names[i]] = {"rate": rate, "divider": div.value[0]}

        config["output_clocks"] = output_cfg
        return config

    def _setup_solver_constraints(self, vcxo):
        """Apply constraints to solver model"""
        self.vcxo = vcxo
        self.config = {
            "r2": self._convert_input(self._r2, "r2"),
            "n2": self._convert_input(self._n2, "n2"),
        }
        # self.config = {"r2": self.model.Var(integer=True, lb=1, ub=4095, value=1)}
        # self.config["n2"] = self.model.Var(
        #     integer=True, lb=8, ub=4095
        # )  # FIXME: CHECK UB

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

    def set_requested_clocks(self, vcxo, out_freqs, clk_names):
        """set_requested_clocks: Define necessary clocks to be generated in model

        Parameters:
            vcxo:
                VCXO frequency in hertz
            out_freqs:
                list of required clocks to be output
        """
        if len(clk_names) != len(out_freqs):
            raise Exception("clk_names is not the same size as out_freqs")
        self._clk_names = clk_names

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
