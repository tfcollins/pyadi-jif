import numpy as np
from adijif.clocks.ad9528_bf import ad9528_bf


class ad9528(ad9528_bf):
    """ AD9528 Model """

    # Ranges
    """ VCO divider """
    m1_available = [3, 4, 5]
    """ Output dividers """
    d_available = [*range(1, 1024)]
    """ VCXO multiplier """
    n2_available = [*range(12, 256)]
    # N = (PxB) + A, P=4, A==[0,1,2,3], B=[3..63]
    # See table 46 of DS for limits
    """ VCXO dividers """
    r1_available = [*range(1, 32)]

    # State management
    _clk_names = -1

    # Defaults
    _m1 = [3, 4, 5]
    _d = [*range(1, 1024)]
    _n2 = [*range(12, 255)]
    _r1 = [*range(1, 32)]

    # Limits
    vco_min = 3450e6
    vco_max = 4025e6
    pfd_max = 275e6

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
        return self._m2

    @n2.setter
    def n2(self, value):
        self._check_in_range(value, self.n2_available, "n2")
        self._m2 = value

    @property
    def r1(self):
        """ r1: VCXO input dividers """
        return self._r1

    @r1.setter
    def r1(self, value):
        self._check_in_range(value, self.r1_available, "r1")
        self._r1 = value

    def get_config(self):

        if not self._clk_names:
            raise Exception("set_requested_clocks must be called before get_config")

        config = {
            "r1": self.config["r1"].value[0],
            "n2": self.config["n2"].value[0],
            "m1": self.config["m1"].value[0],
            "out_dividers": [x.value[0] for x in self.config["out_dividers"]],
            "output_clocks": [],
        }

        clk = self.vcxo / config["r1"] * config["n2"]

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
            "r1": self._convert_input(self._r1, "r1"),
            "m1": self._convert_input(self._m1, "m1"),
            "n2": self._convert_input(self._n2, "n2"),
        }
        # self.config = {"r1": self.model.Var(integer=True, lb=1, ub=31, value=1)}
        # self.config["m1"] = self.model.Var(integer=True, lb=3, ub=5, value=3)
        # self.config["n2"] = self.model.Var(integer=True, lb=12, ub=255, value=12)

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

        # Add requested clocks to output constraints
        self.config["out_dividers"] = []
        for out_freq in out_freqs:
            # od = self.model.Var(integer=True, lb=1, ub=256, value=1)
            od = self._convert_input(self._d, "d_" + str(out_freq))
            # od = self.model.sos1([n*n for n in range(1,9)])
            self.model.Equations(
                [vcxo / self.config["r1"] * self.config["n2"] / od == out_freq]
            )
            self.config["out_dividers"].append(od)
