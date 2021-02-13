import numpy as np
from adijif.clocks.ad9523_1_bf import ad9523_1_bf


class ad9523_1(ad9523_1_bf):
    """ AD9523-1 Model """

    # Ranges
    m1_available = [3, 4, 5]
    d_available = [*range(1, 1024)]
    n2_available = [12, 16, 17, 20, 21, 22, 24, 25, 26, *range(28, 255)]
    a_available = [*range(0, 4)]
    b_available = [*range(3, 64)]
    # N = (PxB) + A, P=4, A==[0,1,2,3], B=[3..63]
    # See table 46 of DS for limits
    r2_available = list(range(1, 31 + 1))

    # Defaults
    _m1 = [3, 4, 5]
    _d = [*range(1, 1024)]
    _n2 = [12, 16, 17, 20, 21, 22, 24, 25, 26, *range(28, 255)]
    _r2 = list(range(1, 31 + 1))

    # Limits
    vco_min = 2.94e9
    vco_max = 3.1e9
    pfd_max = 259e6

    # State management
    _clk_names = -1

    """ Enable internal VCXO/PLL1 doubler """
    use_vcxo_double = False

    @property
    def m1(self):
        """ m1: VCO divider path 1 """
        return self._m1

    @m1.setter
    def m1(self, value):
        self._check_in_range(value, self.m1_available, "m1")
        self._m1 = value

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
        return self._n2

    @n2.setter
    def n2(self, value):
        self._check_in_range(value, self.n2_available, "n2")
        self._n2 = value

    @property
    def r2(self):
        """ r2: VCXO input dividers """
        return self._r2

    @r2.setter
    def r2(self, value):
        self._check_in_range(value, self.r2_available, "r2")
        self._r2 = value

    def get_config(self):
        """ Extract configurations from solver results """

        if not self._clk_names:
            raise Exception("set_requested_clocks must be called before get_config")

        config = {
            "m1": self._get_val(self.config["m1"]),
            "n2": self._get_val(self.config["n2"]),
            "r2": self._get_val(self.config["r2"]),
            "out_dividers": [x.value[0] for x in self.config["out_dividers"]],
            "output_clocks": [],
        }

        clk = self.vcxo / config["r2"] * config["n2"] / config["m1"]
        # for div in self.config["out_dividers"]:
        #     config["output_clocks"].append(clk / div.value[0])

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
            "m1": self._convert_input(self._m1, "m1"),
            "n2": self._convert_input(self._n2, "n2"),
        }
        # self.config = {"r2": self.model.Var(integer=True, lb=1, ub=31, value=1)}
        # self.config["m1"] = self.model.Var(integer=True, lb=3, ub=5, value=3)
        # self.config["n2"] = self.model.sos1(self.n2_available)

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
        self._setup_solver_constraints(vcxo)

        # FIXME: ADD SPLIT m1 configuration support

        # Add requested clocks to output constraints
        self.config["out_dividers"] = []
        for out_freq in out_freqs:
            # od = self.model.Var(integer=True, lb=1, ub=1023, value=1)
            od = self._convert_input(self._d, "d_" + str(out_freq))
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
