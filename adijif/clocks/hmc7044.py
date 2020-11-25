from adijif.clocks.clock import clock
import numpy as np

# class _prop:
#     def __init__(self, name, default, min, max, step):
#         self._min = min
#         self._max = max
#         self._step = step
#         self._val = default
#         self._name = name

#     def __get__(self, instance, owner):
#         return self._val

#     def __set__(self, instance, value):
#         if self._min > value or self._max < value:
#             raise Exception(
#                 "{} must be {}<={}<={}".format(
#                     self._name, self._min, self._name, self._max
#                 )
#             )
#         self._value = value

class hmc7044(clock):
# class hmc7044:

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

        # M = 1000000
        even =  np.arange(2, 4096, 2, dtype=int)
        odivs = np.append([1, 3, 5], even)

        mod = np.gcd.reduce(np.array(rates, dtype=int))
        vcos = []
        configs = []

        # print ("N2\tR2\tPFD\t\tVCO\t\tOutput Dividers")
        
        for n in range(self.n2_divider_min, self.n2_divider_max):
            for r in range(self.r2_divider_min, self.r2_divider_max):
                # Check VCO in range and output clock a multiple of required reference
                f = vcxo * n / r
                if f >= self.vco_min and f <= self.vco_max:
                    if f % mod == 0:
                        d = f / rates
                        if np.all(np.in1d(d, odivs)) and f not in vcos:
                            if f not in vcos:
                                # print(
                                #     "%d\t%d\t%f\t%d\t\t" % (n, r, vcxo / n / M, f / M),
                                #     d,
                                # )
                                vcos.append(f)

                                config = {'N2':n, 'R2':r, 'VCO':f, 'Divider':d, 'PFD':vcxo / n}
                                configs.append(config)
                                if len(configs) >= find:
                                    return configs

        return configs

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
