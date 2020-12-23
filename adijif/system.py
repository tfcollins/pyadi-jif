import adijif  # pylint: disable=unused-import
import numpy as np
from gekko import GEKKO


class system:
    """ System Manager Class

        Manage requirements from all system components and feed into clock rate
        generation algorithms
    """

    """ All converters shared a common sysref. This requires that all
        converters have the same multiframe clock (LMFC)
    """
    use_common_sysref = False

    enable_converter_clocks = True
    enable_fpga_clocks = True

    Debug_Solver = False

    def __init__(self, conv, clk, fpga, vcxo):

        self.model = GEKKO(remote=False)
        self.vcxo = vcxo
        # FIXME: Do checks

        if isinstance(conv, list):
            self.converter = []
            for c in conv:
                self.converter.append(eval(f"adijif.{c}(self.model)"))
        else:
            self.converter = eval(f"adijif.{conv}(self.model)")
        self.clock = eval(f"adijif.{clk}(self.model)")
        self.fpga = eval(f"adijif.{fpga}(self.model)")
        self.vcxo = vcxo

        # TODO: Add these constraints to solver options
        self.configs_to_find = 1
        self.sysref_sample_clock_ratio = 16
        self.sysref_min_div = 4
        self.sysref_max_div = 2 ** 14

        # self.solver_options = [
        #     "minlp_maximum_iterations 1000",  # minlp iterations with integer solution
        #     "minlp_max_iter_with_int_sol 100",  # treat minlp as nlp
        #     "minlp_as_nlp 0",  # nlp sub-problem max iterations
        #     "nlp_maximum_iterations 5000",  # 1 = depth first, 2 = breadth first
        #     "minlp_branch_method 1",  # maximum deviation from whole number
        #     "minlp_integer_tol 0.05",  # covergence tolerance
        #     "minlp_gap_tol 0.01",
        # ]
        self.solver_options = [
            "minlp_maximum_iterations 100000",  # minlp iterations with integer solution
        ]

    def _filter_sysref(self, cnv_clocks, clock_names, convs):
        cnv_clocks_filters = []
        clock_names_filters = []
        if len(cnv_clocks) > 2:
            if self.use_common_sysref:
                ref = convs[0].multiframe_clock
                for conv in convs:
                    if ref != conv.multiframe_clock:
                        raise Exception(
                            "SYSREF cannot be shared. "
                            + "Converters at different LMFCs."
                            + "\nSet use_common_sysref to False "
                            + "for current rates"
                        )

                for i, clk in enumerate(cnv_clocks):
                    # 1,3,5,... are sysrefs. Keep first 1
                    if i / 2 == int(i / 2) or i == 1:
                        cnv_clocks_filters.append(clk)
                        clock_names_filters.append(clock_names[i])
        else:
            cnv_clocks_filters = cnv_clocks
            clock_names_filters = clock_names

        return cnv_clocks_filters, clock_names_filters

    def solve(self):
        """ Defined clocking requirements in Solver model and start solvers routine
        """

        if not self.enable_converter_clocks and not self.enable_fpga_clocks:
            raise Exception("Converter and/or FPGA clocks must be enabled")

        cnv_clocks = []
        clock_names = []
        if self.enable_converter_clocks:

            convs = (
                self.converter if isinstance(self.converter, list) else [self.converter]
            )
            for conv in convs:
                clk = conv.get_required_clocks()
                names = conv.get_required_clock_names()
                if not isinstance(clk, list):
                    clk = [clk]
                if not isinstance(names, list):
                    names = [names]
                cnv_clocks += clk
                clock_names += names
            # Filter out multiple sysrefs
            cnv_clocks_filters, clock_names_filters = self._filter_sysref(
                cnv_clocks, clock_names, convs
            )

        if self.enable_fpga_clocks:
            self.fpga.setup_by_dev_kit_name("zc706")
            fpga_dev_clock = self.fpga.get_required_clocks_qpll(self.converter)
            if not isinstance(fpga_dev_clock, list):
                fpga_dev_clock = [fpga_dev_clock]
        else:
            fpga_dev_clock = []

        # Collect all requirements
        # print("Requested clocks:", cnv_clocks_filters + fpga_dev_clock)
        self.clock.set_requested_clocks(self.vcxo, cnv_clocks_filters + fpga_dev_clock)

        # Set up solver
        self.model.options.SOLVER = 1  # APOPT solver
        # self.model.options.SOLVER = 3  # 1 APOPT, 2 BPOPT, 3 IPOPT
        # self.model.options.IMODE = 5   # simultaneous estimation
        self.model.solver_options = self.solver_options
        self.model.solve(disp=self.Debug_Solver)

    def determine_clocks(self):
        """ Defined clocking requirements and search over all possible dividers
            for working configuration
        """

        # Extract dependent rates from converter
        rates = self.converter.device_clock_available()

        out = []
        for rate in rates:
            rate = np.array(rate, dtype=int)

            # Search across clock chip settings for supported modes
            clk_configs = self.clock.find_dividers(
                self.vcxo, rate, find=self.configs_to_find
            )

            # Find FPGA PLL settings that meet Lane rate
            # requirements based on available reference clocks
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
                    sysref_rate = self._determine_sysref(refs)
                    clk_config["sysref_rate"] = sysref_rate
                    complete_clock_configs.append(clk_config)
                except:  # pylint: disable=bare-except
                    continue

            if not complete_clock_configs:
                continue
                # raise Exception("No valid configurations possible for sysref")
            out.append({"Converter": rate, "ClockChip": complete_clock_configs})

        if not out:
            raise Exception("No valid configurations possible converter sample rate")

        return out

    def _determine_sysref(self, refs):

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
