from dt import dt


class ad9528_dt(dt):
    compatible = "adi,ad9528"

    # reg = <0>;

    # #address-cells = <1>;
    # #size-cells = <0>;

    # spi-max-frequency = <10000000>;
    # //adi,spi-3wire-enable;

    # clock-output-names = "ad9528-1_out0", "ad9528-1_out1", "ad9528-1_out2", "ad9528-1_out3", "ad9528-1_out4", "ad9528-1_out5", "ad9528-1_out6", "ad9528-1_out7", "ad9528-1_out8", "ad9528-1_out9", "ad9528-1_out10", "ad9528-1_out11", "ad9528-1_out12", "ad9528-1_out13";
    # #clock-cells = <1>;

    # adi,vcxo-freq = <122880000>;

    # adi,refa-enable;
    # adi,refa-diff-rcv-enable;
    # adi,refa-r-div = <1>;
    # adi,osc-in-cmos-neg-inp-enable;

    # /* PLL1 config */
    # adi,pll1-feedback-div = <4>;
    # adi,pll1-charge-pump-current-nA = <5000>;

    # /* PLL2 config */
    # adi,pll2-vco-div-m1 = <3>; /* use 5 for 184320000 output device clock */
    # adi,pll2-n2-div = <10>; /* N / M1 */
    # adi,pll2-r1-div = <1>;
    # adi,pll2-charge-pump-current-nA = <805000>;

    # /* SYSREF config */
    # adi,sysref-src = <SYSREF_SRC_INTERNAL>;
    # adi,sysref-pattern-mode = <SYSREF_PATTERN_CONTINUOUS>;
    # adi,sysref-k-div = <512>;
    # adi,sysref-request-enable;
    # adi,sysref-nshot-mode = <SYSREF_NSHOT_4_PULSES>;
    # adi,sysref-request-trigger-mode = <SYSREF_LEVEL_HIGH>;

    # adi,rpole2 = <RPOLE2_900_OHM>;
    # adi,rzero = <RZERO_1850_OHM>;
    # adi,cpole1 = <CPOLE1_16_PF>;

    # adi,status-mon-pin0-function-select = <1>; /* PLL1 & PLL2 Locked */
    # adi,status-mon-pin1-function-select = <7>; /* REFA Correct */