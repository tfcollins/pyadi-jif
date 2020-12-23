from adijif.fpgas.xilinx_bf import xilinx_bf


class xilinx(xilinx_bf):

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

    """ Force use of QPLL for transceiver source """
    force_qpll = 0

    """ Force use of CPLL for transceiver source """
    force_cpll = 0

    """ Force all transceiver sources to be from a single PLL quad.
        This will try to leverage the output dividers of the PLLs
    """
    force_single_quad_tile = 0

    """ Request that clock chip generated device clock
        device clock == LMFC/40
        NOTE: THIS IS NOT FPGA REF CLOCK
    """
    request_device_clock = False

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

    def get_config(self):
        """ Helper function for model to extract solved parameters
            in a readable way
        """
        out = []
        for config in self.configs:
            pll_config = {}
            if config["qpll_0_cpll_1"].value[0]:
                pll_config["type"] = "cpll"
                pll_config["m"] = config["m_cpll"].value[0]
                pll_config["d"] = config["d_cpll"].value[0]
                pll_config["n1"] = config["n1_cpll"].value[0]
                pll_config["n2"] = config["n2_cpll"].value[0]
                pll_config["vco"] = config["vco_cpll"].value[0]
            else:
                pll_config["type"] = "qpll"
                pll_config["m"] = config["m"].value[0]
                pll_config["d"] = config["d"].value[0]
                pll_config["n"] = config["n"].value[0]
                pll_config["vco"] = config["vco"].value[0]
                pll_config["band"] = config["band"].value[0]
                pll_config["qty4_full_rate_enabled"] = config[
                    "qty4_full_rate_enabled"
                ].value[0]
            out.append(pll_config)
        if len(out) == 1:
            out = out[0]
        return out

    def _setup_quad_tile(self, converter, fpga_ref):
        config = {}
        # QPLL
        config["m"] = self.model.Var(integer=True, lb=1, ub=4, value=1)
        config["d"] = self.model.sos1([1, 2, 4, 8, 16])
        config["n"] = self.model.sos1(self.N)

        config["vco"] = self.model.Intermediate(fpga_ref * config["n"] / config["m"])

        # Define QPLL band requirements
        config["band"] = self.model.Var(integer=True, lb=0, ub=1)
        config["vco_max"] = self.model.Intermediate(
            config["band"] * self.vco1_max + (1 - config["band"]) * self.vco0_max
        )
        config["vco_min"] = self.model.Intermediate(
            config["band"] * self.vco1_min + (1 - config["band"]) * self.vco0_min
        )

        # Define if we can use GTY (is available) at full rate
        if self.transciever_type != "GTY4":
            config["qty4_full_rate_divisor"] = self.model.Const(value=1)
        else:
            config["qty4_full_rate_divisor"] = self.model.Var(integer=True, lb=1, ub=2)
        config["qty4_full_rate_enabled"] = self.model.Intermediate(
            1 - config["qty4_full_rate_divisor"]
        )

        #######################
        # CPLL
        config["m_cpll"] = self.model.Var(integer=True, lb=1, ub=2, value=1)
        config["d_cpll"] = self.model.sos1([1, 2, 4, 8])
        config["n1_cpll"] = self.model.Var(integer=True, lb=4, ub=5, value=5)
        config["n2_cpll"] = self.model.Var(integer=True, lb=1, ub=5, value=1)

        config["vco_cpll"] = self.model.Intermediate(
            fpga_ref * config["n1_cpll"] * config["n2_cpll"] / config["m_cpll"]
        )

        # Merge
        if self.force_qpll and self.force_cpll:
            raise Exception("Cannot force both CPLL and QPLL")
        if self.force_qpll:
            config["qpll_0_cpll_1"] = self.model.Const(value=0)
        elif self.force_cpll:
            if converter.bit_clock > self.vco_max * 2:
                raise Exception(f"CPLL too slow for lane rate. Max: {2*self.vco_max}")
            config["qpll_0_cpll_1"] = self.model.Const(value=1)
        else:
            config["qpll_0_cpll_1"] = self.model.Var(integer=True, lb=0, ub=1, value=0)

        config["vco_select"] = self.model.Intermediate(
            config["qpll_0_cpll_1"] * config["vco_cpll"]
            + config["vco"] * (1 - config["qpll_0_cpll_1"])
        )
        config["vco_min_select"] = self.model.Intermediate(
            config["qpll_0_cpll_1"] * self.vco_min
            + config["vco_min"] * (1 - config["qpll_0_cpll_1"])
        )
        config["vco_max_select"] = self.model.Intermediate(
            config["qpll_0_cpll_1"] * self.vco_max
            + config["vco_max"] * (1 - config["qpll_0_cpll_1"])
        )

        config["d_select"] = self.model.Intermediate(
            config["qpll_0_cpll_1"] * config["d_cpll"]
            + (1 - config["qpll_0_cpll_1"]) * config["d"]
        )

        config["rate_divisor_select"] = self.model.Intermediate(
            config["qpll_0_cpll_1"] * (2)
            + (1 - config["qpll_0_cpll_1"]) * config["qty4_full_rate_divisor"]
        )
        #######################

        # Set all relations
        # QPLL+CPLL
        self.model.Equations(
            [
                config["vco_select"] >= config["vco_min_select"],
                config["vco_select"] <= config["vco_max_select"],
                config["vco_select"] * config["rate_divisor_select"]
                == converter.bit_clock * config["d_select"],
            ]
        )
        return config

    def get_required_clocks(self, converter):
        """ get_required_clocks: Get necessary clocks for QPLL/CPLL configuration

            Parameters:
                converter:
                    Converter object of converter connected to FPGA
        """
        if not isinstance(converter, list):
            converter = [converter]

        self.config = {
            "fpga_ref": self.model.Var(
                integer=True,
                lb=self.ref_clock_min,
                ub=self.ref_clock_max,
                value=self.ref_clock_min,
            )
        }

        # https://www.xilinx.com/support/documentation/user_guides/ug476_7Series_Transceivers.pdf

        if self.force_single_quad_tile:
            raise Exception("force_single_quad_tile==1 not implemented")
        else:
            #######################
            self.configs = []
            self.dev_clocks = []
            for cnv in converter:
                config = self._setup_quad_tile(cnv, self.config["fpga_ref"])
                # Set optimizations
                # self.model.Obj(self.config["d"])
                # self.model.Obj(self.config["d_cpll"])
                self.model.Obj(config["d_select"])
                self.model.Obj(-1 * config["qpll_0_cpll_1"])  # Favor CPLL over QPLL
                self.configs.append(config)
                # FPGA also requires clock at device clock rate
                if self.request_device_clock:
                    self.dev_clocks.append(cnv.device_clock)

        self.model.Obj(self.config["fpga_ref"])

        return [self.config["fpga_ref"]] + self.dev_clocks
