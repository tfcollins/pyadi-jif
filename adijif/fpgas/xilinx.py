from adijif.fpgas.fpga import fpga


class xilinx(fpga):

    hdl_core_version = 1.0

    available_speed_grades = [-1, -2, -3]
    speed_grade = -2

    transceiver_voltage = 800

    available_fpga_packages = [
        "Unknown",
        "RF",
        "FL",
        "FF",
        "FB",
        "HC",
        "FH",
        "CS",
        "CP",
        "FT",
        "FG",
        "SB",
        "RB",
        "RS",
        "CL",
        "SF",
        "BA",
        "FA",
    ]
    fpga_package = "FB"

    available_fpga_families = ["Unknown", "Artix", "Kintex", "Virtex", "Zynq"]
    fpga_family = "Zynq"

    available_transceiver_types = ["GTX2"]
    transciever_type = "GTX2"

    sys_clk_selections = [
        "GTH34_SYSCLK_CPLL",
        "GTH34_SYSCLK_QPLL1",
        "GTH34_SYSCLK_QPLL0",
    ]
    sys_clk_select = "GTH34_SYSCLK_QPLL1"

    force_qpll = 0
    force_cpll = 0

    @property
    def ref_clock_max(self):
        # https://www.xilinx.com/support/documentation/data_sheets/ds191-XC7Z030-XC7Z045-data-sheet.pdf
        if self.transciever_type == "GTX2":
            if self.speed_grade == "-3E":
                return 700000000
            else:
                return 670000000
        else:
            raise Exception(
                f"Unknown ref_clock_max for transceiver {self.transciever_type}"
            )
            # raise Exception(f"Unknown transceiver type {self.transciever_type}")

    @property
    def ref_clock_min(self):
        # https://www.xilinx.com/support/documentation/data_sheets/ds191-XC7Z030-XC7Z045-data-sheet.pdf
        if self.transciever_type == "GTX2":
            return 60000000
        else:
            raise Exception(
                f"Unknown ref_clock_max for transceiver {self.transciever_type}"
            )
            # raise Exception(f"Unknown transceiver type {self.transciever_type}")

    # CPLL
    @property
    def vco_min(self):
        if self.transciever_type == "GTX2":
            return 1600000000
        elif self.transciever_type in ["GTH3", "GTH4", "GTY4"]:
            return 2000000000
        else:
            raise Exception(f"Unknown transceiver type {self.transciever_type}")

    @property
    def vco_max(self):
        if self.transciever_type == "GTX2":
            return 3300000000
        elif self.transciever_type in ["GTH3", "GTH4", "GTY4"]:
            if self.hdl_core_version > 2:
                if self.transciever_type in ["GTH3", "GTH4"]:
                    if self.transceiver_voltage < 850 or self.speed_grade == -1:
                        return 4250000000
                elif self.transciever_type == "GTY4" and self.speed_grade == -1:
                    return 4250000000
            return 6250000000
        else:
            raise Exception(f"Unknown transceiver type {self.transciever_type}")

    # QPLL
    @property
    def vco0_min(self):
        if self.transciever_type == "GTX2":
            return 5930000000
        elif self.transciever_type in ["GTH3", "GTH4", "GTY4"]:
            if self.sys_clk_select == "GTH34_SYSCLK_QPLL1":
                return 8000000000
            else:
                return 9800000000
        else:
            raise Exception(f"Unknown transceiver type {self.transciever_type}")

    @property
    def vco0_max(self):
        if self.transciever_type == "GTX2":
            if (
                self.hdl_core_version > 2
                and self.fpga_family == "Kintex"
                and self.fpga_package in ["FB", "RF", "FF"]
            ):
                return 6600000000
            return 8000000000
        elif self.transciever_type in ["GTH3", "GTH4", "GTY4"]:
            if self.sys_clk_select == "GTH34_SYSCLK_QPLL1":
                return 13000000000
            else:
                return 16375000000
        else:
            raise Exception(f"Unknown transceiver type {self.transciever_type}")

    @property
    def vco1_min(self):
        if self.transciever_type == "GTX2":
            return 9800000000
        elif self.transciever_type in ["GTH3", "GTH4", "GTY4"]:
            return self.vco0_min
        else:
            raise Exception(f"Unknown transceiver type {self.transciever_type}")

    @property
    def vco1_max(self):
        if self.transciever_type == "GTX2":
            if self.hdl_core_version > 2 and self.speed_grade == -2:
                return 10312500000
            return 12500000000
        elif self.transciever_type in ["GTH3", "GTH4", "GTY4"]:
            return self.vco0_max
        else:
            raise Exception(f"Unknown transceiver type {self.transciever_type}")

    @property
    def N(self):
        if self.transciever_type == "GTX2":
            return [16, 20, 32, 40, 64, 66, 80, 100]
        else:
            raise Exception(f"Unknown transceiver type {self.transciever_type}")

    def setup_by_dev_kit_name(self, name):
        """ Configure object based on board name. Ex: zc706, zcu102 """

        if name.lower() == "zc706":
            self.transciever_type = "GTX2"
            self.fpga_family = "Zynq"
            self.fpga_package = "FF"
            self.speed_grade = -2
        else:
            raise Exception(f"No boardname found in library for {name}")

    def determine_pll(self, bit_clock, fpga_ref_clock):
        """
            Parameters:
                bit_clock:
                    Equivalent to lane rate in bits/second
                fpga_ref_clock:
                    System reference clock
        """
        try:
            info = self.determine_cpll(bit_clock, fpga_ref_clock)
        except:
            info = self.determine_qpll(bit_clock, fpga_ref_clock)
        return info

    def _cpll_model_setup(self, clock, converter):

        self.config = {"m": self.model.Var(integer=True, lb=1, ub=2, value=1)}
        self.config["d"] = self.model.sos1([1, 2, 4, 8])
        self.config["n1"] = self.model.Var(integer=True, lb=4, ub=5, value=1)
        self.config["n2"] = self.model.Var(integer=True, lb=1, ub=5, value=1)

        self.config["vco"] = self.model.Intermediate(
            clock.config["fpga_ref"]
            * self.config["n1"]
            * self.config["n2"]
            / self.config["m"]
        )

        self.model.Equations(
            [
                self.config["vco"] >= self.vco_min,
                self.config["vco"] <= self.vco_max,
                clock.config["fpga_ref"] / self.config["m"] / self.config["d"]
                == converter.bit_clock / (2 * self.config["n1"] * self.config["n2"]),
            ]
        )
        self.model.Obj(self.config["fpga_ref"] * -1)

    def get_required_clocks_qpll(self, converter):
        """ get_required_clocks_qpll: Get necessary clocks for QPLL configuration

            Parameters:
                converter:
                    Converter object of converter connected to FPGA
        """

        self.config = {
            "fpga_ref": self.model.Var(
                integer=True,
                lb=self.ref_clock_min,
                ub=self.ref_clock_max,
                value=self.ref_clock_min,
            )
        }

        # https://www.xilinx.com/support/documentation/user_guides/ug476_7Series_Transceivers.pdf

        # QPLL
        self.config["m"] = self.model.Var(integer=True, lb=1, ub=4, value=1)
        self.config["d"] = self.model.sos1([1, 2, 4, 8, 16])
        self.config["n"] = self.model.sos1(self.N)

        self.config["vco"] = self.model.Intermediate(
            self.config["fpga_ref"] * self.config["n"] / self.config["m"]
        )

        # Define QPLL band requirements
        self.config["band"] = self.model.Var(integer=True, lb=0, ub=1)
        self.config["vco_max"] = self.model.Intermediate(
            self.config["band"] * self.vco1_max
            + (1 - self.config["band"]) * self.vco0_max
        )
        self.config["vco_min"] = self.model.Intermediate(
            self.config["band"] * self.vco1_min
            + (1 - self.config["band"]) * self.vco0_min
        )

        # Define if we can use GTY (is available) at full rate
        if self.transciever_type != "GTY4":
            self.config["qty4_full_rate_divisor"] = self.model.Const(value=1)
        else:
            self.config["qty4_full_rate_divisor"] = self.model.Var(
                integer=True, lb=1, ub=2
            )
        self.config["qty4_full_rate_enabled"] = self.model.Intermediate(
            1 - self.config["qty4_full_rate_divisor"]
        )

        #######################
        # CPLL
        self.config["m_cpll"] = self.model.Var(integer=True, lb=1, ub=2, value=1)
        self.config["d_cpll"] = self.model.sos1([1, 2, 4, 8])
        self.config["n1_cpll"] = self.model.Var(integer=True, lb=4, ub=5, value=5)
        self.config["n2_cpll"] = self.model.Var(integer=True, lb=1, ub=5, value=1)

        self.config["vco_cpll"] = self.model.Intermediate(
            self.config["fpga_ref"]
            * self.config["n1_cpll"]
            * self.config["n2_cpll"]
            / self.config["m_cpll"]
        )

        # Merge
        if self.force_qpll and self.force_cpll:
            raise Exception("Cannot force both CPLL and QPLL")
        if self.force_qpll:
            self.config["qpll_0_cpll_1"] = self.model.Const(value=0)
        elif self.force_cpll:
            if converter.bit_clock > self.vco_max * 2:
                raise Exception(f"CPLL too slow for lane rate. Max: {2*self.vco_max}")
            self.config["qpll_0_cpll_1"] = self.model.Const(value=1)
        else:
            self.config["qpll_0_cpll_1"] = self.model.Var(
                integer=True, lb=0, ub=1, value=0
            )

        self.config["vco_select"] = self.model.Intermediate(
            self.config["qpll_0_cpll_1"] * self.config["vco_cpll"]
            + self.config["vco"] * (1 - self.config["qpll_0_cpll_1"])
        )
        self.config["vco_min_select"] = self.model.Intermediate(
            self.config["qpll_0_cpll_1"] * self.vco_min
            + self.config["vco_min"] * (1 - self.config["qpll_0_cpll_1"])
        )
        self.config["vco_max_select"] = self.model.Intermediate(
            self.config["qpll_0_cpll_1"] * self.vco_max
            + self.config["vco_max"] * (1 - self.config["qpll_0_cpll_1"])
        )

        self.config["d_select"] = self.model.Intermediate(
            self.config["qpll_0_cpll_1"] * self.config["d_cpll"]
            + (1 - self.config["qpll_0_cpll_1"]) * self.config["d"]
        )

        self.config["rate_divisor_select"] = self.model.Intermediate(
            self.config["qpll_0_cpll_1"] * (2)
            + (1 - self.config["qpll_0_cpll_1"]) * self.config["qty4_full_rate_divisor"]
        )
        #######################

        # Set all relations
        # QPLL+CPLL
        self.model.Equations(
            [
                self.config["vco_select"] >= self.config["vco_min_select"],
                self.config["vco_select"] <= self.config["vco_max_select"],
                self.config["vco_select"] * self.config["rate_divisor_select"]
                == converter.bit_clock * self.config["d_select"],
            ]
        )

        # QPLL ONLY
        # self.model.Equations(
        #     [
        #         self.config["vco"] >= self.config["vco_min"],
        #         self.config["vco"] <= self.config["vco_max"],
        #         self.config["vco"] / self.config["d"]
        #         == converter.bit_clock / self.config["qty4_full_rate_divisor"],
        #     ]
        # )

        # CPLL ONLY
        # self.model.Equations(
        #     [
        #         self.config["vco_cpll"] >= self.vco_min,
        #         self.config["vco_cpll"] <= self.vco_max,
        #         2 * self.config["vco_cpll"]
        #         == converter.bit_clock * self.config["d_cpll"],
        #     ]
        # )

        # Set optimizations
        # self.model.Obj(self.config["d"])
        # self.model.Obj(self.config["d_cpll"])
        self.model.Obj(self.config["d_select"])

        self.model.Obj(self.config["fpga_ref"])

        return self.config["fpga_ref"]

    def determine_cpll(self, bit_clock, fpga_ref_clock):
        """
            Parameters:
                bit_clock:
                    Equivalent to lane rate in bits/second
                fpga_ref_clock:
                    System reference clock
        """
        assert isinstance(bit_clock, int), "bit_clock must be an int"
        assert isinstance(fpga_ref_clock, int), "fpga_ref_clock must be an int"

        # VCO = ( REF_CLK * N1 * N2 ) / M
        # bit_clock = ( VCO * 2 ) / D

        for m in [1, 2]:
            for d in [1, 2, 4, 8]:
                for n1 in [5, 4]:
                    for n2 in [5, 4, 3, 2, 1]:
                        vco = fpga_ref_clock * n1 * n2 / m
                        # print("VCO", self.vco_min/1e9, vco/1e9, self.vco_max/1e9)
                        if vco > self.vco_max or vco < self.vco_min:
                            continue
                        # print("VCO", vco)
                        # fpga_lane_rate = vco * 2 / d
                        # print("lane rate", fpga_lane_rate)

                        # VCO == 5,10,20,40 GHz

                        # print(fpga_ref_clock / m / d, bit_clock / (2 * n1 * n2))
                        if fpga_ref_clock / m / d == bit_clock / (2 * n1 * n2):
                            return {
                                "vco": vco,
                                "d": d,
                                "m": m,
                                "n1": n1,
                                "n2": n2,
                                "type": "CPLL",
                            }

        raise Exception("No valid CPLL configuration found")

    def determine_qpll(self, bit_clock, fpga_ref_clock):
        """
            Parameters:
                bit_clock:
                    Equivalent to lane rate in bits/second
                fpga_ref_clock:
                    System reference clock
        """

        if self.ref_clock_max < fpga_ref_clock or fpga_ref_clock < self.ref_clock_min:
            raise Exception("fpga_ref_clock not within range")

        for m in [1, 2, 3, 4]:
            for d in [1, 2, 4, 8, 16]:
                for n in self.N:
                    vco = fpga_ref_clock * n / m
                    if self.vco1_min <= vco <= self.vco1_max:
                        band = 1
                    elif self.vco0_min <= vco <= self.vco0_max:
                        band = 0
                    else:
                        continue

                    if fpga_ref_clock / m / d == bit_clock / n:
                        return {
                            "vco": vco,
                            "band": band,
                            "d": d,
                            "m": m,
                            "n": n,
                            "qty4_full_rate": 0,
                            "type": "QPLL",
                        }

                    if self.transciever_type != "GTY4":
                        continue

                    if fpga_ref_clock / m / d == bit_clock / 2 / n:
                        return {
                            "vco": vco,
                            "band": band,
                            "d": d,
                            "m": m,
                            "n": n,
                            "qty4_full_rate": 1,
                            "type": "QPLL",
                        }

        raise Exception("No valid QPLL configuration found")
