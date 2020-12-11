import numpy as np
from adijif.clocks.clock import clock


class hmc7044(clock):

    pre_scaler_min = 1
    pre_scaler_max = 255

    vcxo_scaler_min = 1
    vcxo_scaler_max = 255

    r1_divider_min = 1
    r1_divider_max = 65535

    n1_divider_min = 1
    n1_divider_max = 65535

    r2_divider_min = 1
    r2_divider_max = 4095

    n2_divider_min = 8
    n2_divider_max = 65535

    vco_min = 2150e6
    vco_max = 3550e6

    osc_divider_options = [1, 2, 4, 8]

    use_vcxo_double = True

    def __init__(self):
        pass

    def find_dividers(self, vcxo, rates, find=3):

        if self.use_vcxo_double:
            vcxo *= 2

        even = np.arange(2, 4096, 2, dtype=int)
        odivs = np.append([1, 3, 5], even)

        mod = np.gcd.reduce(np.array(rates, dtype=int))
        vcos = []
        configs = []

        for n in range(self.n2_divider_min, self.n2_divider_max):
            for r in range(self.r2_divider_min, self.r2_divider_max):
                # Check VCO in range and output clock a multiple of required reference
                f = vcxo * n / r
                if f >= self.vco_min and f <= self.vco_max:
                    # Check if required dividers for output clocks are in set
                    if f % mod == 0:
                        d = f / rates
                        if np.all(np.in1d(d, odivs)) and f not in vcos:
                            if f not in vcos:
                                vcos.append(f)
                                config = {
                                    "N2": n,
                                    "R2": r,
                                    "VCO": f,
                                    "Divider": d,
                                    "PFD": vcxo / n,
                                }
                                configs.append(config)
                                if len(configs) >= find:
                                    return configs

        return configs

    def check_sysref_divider(self, configs, ratio):
        valid = []
        even = np.arange(2, 4096, 2, dtype=int)
        odivs = np.append([1, 3, 5], even)

        for config in configs:
            d = config["Divider"]
            print(d)
            required = d * ratio
            if required in odivs:
                valid.append(config)

        if not valid:
            raise Exception(
                "SYSREF to sample clock ratio not possible based on required ratio {}".format(
                    required
                )
            )
        return valid

    def all_params(self):
        pass
        # Target dependent
        # adi,jesd204-max-sysref-frequency-hz = <2000000>; /* 2 MHz */

        # VCXO Dependent


# adi,vcxo-frequency = <122880000>;
# adi,pll1-clkin-frequencies = <122880000 30720000 0 0>;

# adi,pll1-loop-bandwidth-hz = <200>;


# adi,pll2-output-frequency = <3100000000>;

# adi,sysref-timer-divider = <1024>;
# adi,pulse-generator-mode = <0>;

# adi,clkin0-buffer-mode  = <0x07>;
# adi,clkin1-buffer-mode  = <0x07>;
# adi,oscin-buffer-mode = <0x15>;
