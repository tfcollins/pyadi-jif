import adijif
import numpy as np
from gekko import GEKKO


class system:
    def __init__(self, conv, clk, fpga, vcxo):

        self.model = GEKKO()
        self.vcxo = vcxo
        # FIXME: Do checks

        self.converter = eval(f"adijif.{conv}(self.model)")
        self.clock = eval(f"adijif.{clk}(self.model)")
        self.fpga = eval(f"adijif.{fpga}(self.model)")
        self.vcxo = vcxo
        self.configs_to_find = 3
        self.sysref_sample_clock_ratio = 16
        self.sysref_min_div = 4
        self.sysref_max_div = 2 ** 14

        self.enable_converter_clocks = True
        self.enable_fpga_clocks = True
        self.Debug_Solver = False

    def solve(self):

        if not self.enable_converter_clocks and not self.enable_fpga_clocks:
            raise Exception("Converter and/or FPGA clocks must be enabled")

        if self.enable_converter_clocks:
            cnv_clocks = self.converter.get_required_clocks()
        else:
            cnv_clocks = []

        if self.enable_fpga_clocks:
            self.fpga.setup_by_dev_kit_name("zc706")
            fpga_dev_clock = self.fpga.get_required_clocks_qpll(self.converter)
            if not isinstance(fpga_dev_clock, list):
                fpga_dev_clock = [fpga_dev_clock]
        else:
            fpga_dev_clock = []

        # Collect all requirements
        self.clock.set_requested_clocks(self.vcxo, fpga_dev_clock + cnv_clocks)

        self.model.options.SOLVER = 1  # APOPT solver
        self.model.solve(disp=self.Debug_Solver)
        self.model.solver_options = [
            "minlp_maximum_iterations 1000",  # minlp iterations with integer solution
            "minlp_max_iter_with_int_sol 100",  # treat minlp as nlp
            "minlp_as_nlp 0",  # nlp sub-problem max iterations
            "nlp_maximum_iterations 5000",  # 1 = depth first, 2 = breadth first
            "minlp_branch_method 1",  # maximum deviation from whole number
            "minlp_integer_tol 0.05",  # covergence tolerance
            "minlp_gap_tol 0.01",
        ]

    def determine_clocks2(self):

        # Get ranges based on required sample rate and other configs
        cnv_dc_min, cnv_dc_max = self.converter.device_clock_ranges()
        cnv_sr_min, cnv_sr_max = self.converter.sysref_clock_ranges()
        print(cnv_dc_min, cnv_dc_max)
        print(cnv_sr_min, cnv_sr_max)
        print("bit clock", self.converter.bit_clock)

        clk = cnv_sr_min
        while clk <= cnv_sr_max:
            print(clk)
            try:
                d = self.fpga.determine_cpll(self.converter.bit_clock, clk)
                print(d)
                print("Working")
                break
            except:
                clk = clk * 2

        clk = cnv_sr_min
        while clk <= cnv_sr_max:
            print(clk)
            try:
                d = self.fpga.determine_qpll(self.converter.bit_clock, clk)
                print(d)
                print("Working")
                break
            except:
                clk = clk * 2

    def _gen_clock_type(self, name, end_point, rate, config):
        return {"name": name, "end_point": end_point, "rate": rate, "config": config}

    def determine_clocks(self):
        # rates = [self.converter.device_clock, self.converter.multiframe_clock]
        # rates = [self.converter.sample_clock, self.converter.multiframe_clock]

        # Extract dependent rates from converter
        try:
            rates = self.converter.device_clock_available()
        except:
            # FIXME
            rates = self.converter.device_clock_ranges()

        out = []
        for rate in rates:
            rate = np.array(rate, dtype=int)

            # Search across clock chip settings for supported modes
            clk_configs = self.clock.find_dividers(
                self.vcxo, rate, find=self.configs_to_find
            )

            # Find FPGA PLL settings that meet Lane rate requirements based on available reference clocks
            valid_clock_configs = []
            for clk_config in clk_configs:
                print("clk_config", clk_config)
                refs = self.clock.list_possible_references(clk_config)
                for ref in refs:
                    try:
                        info = self.fpga.determine_pll(self.converter.bit_clock, ref)
                        break
                    except:
                        ref = False
                        continue

                if ref:
                    clk_config["fpga_pll_config"] = info
                    valid_clock_configs.append(clk_config)

            if not valid_clock_configs:
                continue
                # raise Exception("No valid configurations possible for FPGA")

            # Check available output dividers for sysref required
            complete_clock_configs = []
            for clk_config in valid_clock_configs:
                refs = self.clock.list_possible_references(clk_config)
                try:
                    sysref_rate = self.determine_sysref(refs)
                    clk_config["sysref_rate"] = sysref_rate
                    complete_clock_configs.append(clk_config)
                except:
                    continue

            if not complete_clock_configs:
                continue
                # raise Exception("No valid configurations possible for sysref")
            out.append({"Converter": rate, "ClockChip": complete_clock_configs})

            # Organize
            # cnv_rate = rates
            # converter_clock = self._gen_clock_type("direct_converter_clock",self.converter.name,cnv_rate,[])

        if not out:
            raise Exception("No valid configurations possible converter sample rate")

        return out

    def determine_sysref(self, refs):

        lmfc = self.converter.multiframe_clock
        div = self.sysref_min_div

        while div < self.sysref_max_div:
            sysref_rate = lmfc / div
            if sysref_rate in refs:
                # vco_div = cfs[0]['vco']/sysref/cfs[0]['m1']
                # print("FOUND")
                break
            else:
                sysref_rate = False
            div *= 2

        if not sysref_rate:
            raise Exception("No possible sysref found")

        return sysref_rate
