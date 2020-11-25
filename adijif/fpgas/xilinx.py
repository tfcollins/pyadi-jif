from adijif.fpgas.fpga import fpga

class xilinx(fpga):

    hdl_core_version = 3

    available_speed_grades = [-1, -2, -3]
    speed_grade = -2

    transceiver_voltage = 800

    available_fpga_packages = [
        "UNKNOWN",
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

    available_fpga_families = ["UNKNOWN","Artix", "Kintex", "Virtex", "Zynq"]
    fpga_family = "Zynq"

    available_transceiver_types = ["GTX2"]
    transciever_type = "GTX2"

    sys_clk_selections = [
        "GTH34_SYSCLK_CPLL",
        "GTH34_SYSCLK_QPLL1",
        "GTH34_SYSCLK_QPLL0",
    ]
    sys_clk_select = "GTH34_SYSCLK_QPLL1"

    def __init__(self):
        pass

    # CPLL
    @property
    def vco_min(self):
        if self.transciever_type == "GTX2":
            return 1600000
        elif self.transciever_type in ["GTH3", "GTH3", "GTY4"]:
            return 2000000
        else:
            raise Exception("Unknown transceiver type {self.transciever_type}")

    @property
    def vco_max(self):
        if self.transciever_type == "GTX2":
            return 3300000
        elif self.transciever_type in ["GTH3", "GTH3", "GTY4"]:
            if self.hdl_core_version > 2:
                if self.transciever_type in ["GTH3", "GTH3"]:
                    if self.transceiver_voltage < 850 or self.speed_grade == -1:
                        return 4250000
                elif self.transciever_type == "GTY4" and self.speed_grade == -1:
                    return 4250000
            return 6250000
        else:
            raise Exception("Unknown transceiver type {self.transciever_type}")

    # QPLL
    @property
    def vco0_min(self):
        if self.transciever_type == "GTX2":
            return 5930000
        elif self.transciever_type in ["GTH3", "GTH3", "GTY4"]:
            if self.sys_clk_select == "GTH34_SYSCLK_QPLL1":
                return 8000000
            else:
                return 9800000
        else:
            raise Exception("Unknown transceiver type {self.transciever_type}")

    @property
    def vco0_max(self):
        if self.transciever_type == "GTX2":
            if (
                self.hdl_core_version > 2
                and self.fpga_family == "Kintex"
                and self.fpga_package in ["FB", "RF", "FF"]
            ):
                return 6600000
            return 8000000
        elif self.transciever_type in ["GTH3", "GTH3", "GTY4"]:
            if self.sys_clk_select == "GTH34_SYSCLK_QPLL1":
                return 13000000
            else:
                return 16375000
        else:
            raise Exception("Unknown transceiver type {self.transciever_type}")

    @property
    def vco1_min(self):
        if self.transciever_type == "GTX2":
            return 9800000
        elif self.transciever_type in ["GTH3", "GTH3", "GTY4"]:
            return self.vco0_min
        else:
            raise Exception("Unknown transceiver type {self.transciever_type}")

    @property
    def vco1_max(self):
        if self.transciever_type == "GTX2":
            if self.hdl_core_version > 2 and self.speed_grade == -2:
                return 10312500
            return 12500000
        elif self.transciever_type in ["GTH3", "GTH3", "GTY4"]:
            return self.vco0_max
        else:
            raise Exception("Unknown transceiver type {self.transciever_type}")

    @property
    def N(self):
        if self.transciever_type == "GTX2":
            return [16, 20, 32, 40, 64, 66, 80, 100]
        else:
            raise Exception("Unknown transceiver type {self.transciever_type}")

    def determine_cpll(self, bit_clock, sysref_clock):
        """
            Parameters:
                bit_clock: 
                    Equivalent to lane rate in bits/second
                sysref_clock:
                    System reference clock
        """

        # VCO = ( REF_CLK * N1 * N2 ) / M
        # bit_clock = ( VCO * 2 ) / D

        for m in [1, 2]:
            for d in [1, 2, 4, 8]:
                for n1 in [5, 4]:
                    for n2 in [5, 4, 3, 2, 1]:
                        vco = sysref_clock * n1 * n2 / m
                        if vco > self.vco_max or vco < self.vco_min:
                            continue
                        if sysref_clock / m / d == bit_clock / (2 * n1 * n2):
                            return d, m, n1, n2

        raise Exception("No valid CPLL configuration found")

    def determine_qpll(self, bit_clock, sysref_clock):
        """
            Parameters:
                bit_clock: 
                    Equivalent to lane rate in bits/second
                sys_clock:
                    System clock
                sysref_clock:
                    System reference clock
        """

        #  Ref: https://www.xilinx.com/support/documentation/user_guides/ug476_7Series_Transceivers.pdf
        #  Page: 55
        #     Vco_Freq = (refclk_khz * n) / m
        #  LineRate = Vco_Freq / d

        #  Make sure to not confuse Vco_Freq with fPLLClkout.
        #  fPLLClkout = (refclk_khz * n) / (m * 2), so technically Vco_Freq = 2 * fPLLClkout
        #  And the 2 is reduced in both equations.

        # VCO = ( REF_CLK * N ) / M
        # bit_clock = ( VCO ) / D

        for m in [1, 2, 3, 4]:
            for d in [1, 2, 4, 8, 16]:
                for n in self.N:
                    vco = sysref_clock * n / m
                    if self.vco1_min <= vco <= self.vco1_max:
                        band = 1
                    elif self.vco0_min <= vco <= self.vco0_max:
                        band = 0
                    else:
                        continue

                    if sysref_clock / m / d == bit_clock / n:
                        return band, d, m, n, 0

                    if self.transciever_type != "GTY4":
                        continue

                    if sysref_clock / m / d == bit_clock / 2 / n:
                        return band, d, m, n, 1

        raise Exception("No valid QPLL configuration found")
