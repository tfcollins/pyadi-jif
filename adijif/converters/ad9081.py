"""AD9081 high speed MxFE clocking model."""
from abc import ABCMeta, abstractmethod
from typing import Dict, List, Union

from docplex.cp.model import CpoModel  # type: ignore
from gekko import GEKKO  # type: ignore

from adijif.converters.converter import converter


class ad9081_core(metaclass=ABCMeta):
    """AD9081 high speed MxFE model.

    This model supports both direct clock configurations and on-board
    generation

    Clocking: AD9081 can internally generate or leverage external clocks. The
    high speed clock within the system is referred to as the DAC clock and
    the ADC clock will be a divided down version of the clock:
        adc_clock  == dac_clock / L, where L = 1,2,3,4


    For internal generation, the DAC clock is generated through an integer PLL
    through the following relation:
        dac_clock == ((m_vco * n_vco) / R * ref_clock) / D

    For external clocks, the clock must be provided at the DAC clock rate

    Once we have the DAC clock the data rates can be directly evaluated into
    each JESD framer:

    rx_baseband_sample_rate = (dac_clock / L) / datapath_decimation
    tx_baseband_sample_rate = dac_clock / datapath_interpolation

    """

    device_clock_available = None
    device_clock_ranges = None

    model: Union[GEKKO, CpoModel] = None

    name = "AD9081"

    direct_clocking = True
    use_direct_clocking = True

    l_possible = [1, 2, 3, 4]
    l = 1  # pylint:  disable=E741
    m_vco_possible = [5, 7, 8, 11]  # 8 is nominal
    m_vco = 8
    n_vco_possible = [*range(2, 50 + 1)]
    n_vco = 2
    r_possible = [1, 2, 3, 4]
    r = 1
    d_possible = [1, 2, 3, 4]
    d = 1

    available_jesd_modes = ["jesd204b", "jesd204c"]

    # FIXME
    K_possible = [4, 8, 12, 16, 20, 24, 28, 32]
    L_possible = [1, 2, 4, 8]
    M_possible = [1, 2, 4, 8]
    N_possible = [*range(7, 16 + 1)]
    Np_possible = [8, 16]
    F_possible = [1, 2, 4, 8, 16]
    CS_possible = [0, 1, 2, 3]
    CF_possible = [0]
    S_possible = [1]  # Not found in DS
    # FIXME

    link_min = [1.5e9, 6e9]  # 204b, 204c
    link_max = [15.5e9, 24.75e9]  # 204b, 204c

    # Input clock requirements
    available_datapath_decimation = [1, 2, 4, 8, 16]  # FIXME
    datapath_decimation = 1
    available_datapath_interpolation = [1, 2, 4, 8, 16]  # FIXME
    datapath_interpolation = 1

    # Internal limits
    pfd_min = 25e6
    pfd_max = 750e6
    vco_min = 6e9
    vco_max = 12e9

    config = {}  # type: ignore

    max_input_clock = 12e9
    _model_type = "adc"

    def get_required_clock_names(self) -> List[str]:
        """Get list of strings of names of requested clocks.

        This list of names is for the clocks defined by get_required_clocks

        Returns:
            List[str]: List of strings of clock names in order
        """
        clk = "ad9081_dac_clock" if self.use_direct_clocking else "ad9081_pll_ref"
        return [clk, "ad9081_sysref"]

    @property
    @abstractmethod
    def _converter_clock_config(self) -> None:
        """Define source clocking relation based on ADC, DAC, or both.

        Raises:
            NotImplementedError: Method not implemented
        """
        raise NotImplementedError

    def _pll_config(self) -> Dict:

        self._converter_clock_config()  # type: ignore

        self.config["ref_clk"] = self.model.Var(
            integer=True, lb=1e6, ub=self.max_input_clock, value=self.max_input_clock
        )
        self.config["m_vco"] = self.model.sos1([5, 7, 8, 11])
        self.config["n_vco"] = self.model.Var(integer=True, lb=2, ub=50, value=2)
        self.config["r"] = self.model.Var(integer=True, lb=1, ub=4, value=1)
        self.config["d"] = self.model.Var(integer=True, lb=1, ub=4, value=1)

        self.config["vco"] = self.model.Intermediate(
            self.config["ref_clk"]
            * self.config["m_vco"]
            * self.config["n_vco"]
            / self.config["r"],
        )

        self.model.Equation(
            [
                self.config["converter_clk"] * self.config["d"] * self.config["r"]
                == self.config["ref_clk"] * self.config["m_vco"] * self.config["n_vco"],
                self.config["vco"] >= self.vco_min,
                self.config["vco"] <= self.vco_max,
                self.config["ref_clk"] / self.config["r"] <= self.pfd_max,
                self.config["ref_clk"] / self.config["r"] >= self.pfd_min,
                self.config["converter_clk"] <= self.max_input_clock,
            ]
        )

        return self.config["ref_clk"]

    def get_required_clocks(self) -> List:
        """Generate list required clocks.

        For AD9081 this will contain [converter clock, sysref requirement SOS]

        Returns:
            List: List of solver variables, equations, and constants

        Raises:
            Exception: If direct clocking is used. Not yet implemented
        """
        # SYSREF
        self.config = {}
        self.config["lmfc_divisor_sysref"] = self.model.Var(
            integer=True, lb=1, ub=20, value=19
        )
        self.config["sysref"] = self.model.Intermediate(
            self.multiframe_clock  # type: ignore
            / (self.config["lmfc_divisor_sysref"] * self.config["lmfc_divisor_sysref"])
        )

        # Device Clocking
        if self.use_direct_clocking:
            raise Exception("Not implemented yet")
            # adc_clk = self.sample_clock * self.datapath_decimation
        else:
            clk = self._pll_config()  # type: ignore

        # Objectives
        # self.model.Obj(self.config["sysref"])  # This breaks many searches
        # self.model.Obj(-1*self.config["lmfc_divisor_sysref"])

        return [clk, self.config["sysref"]]


class ad9081_rx(ad9081_core, converter):
    """AD9081 Receive model."""

    _model_type = "adc"

    def _converter_clock_config(self) -> None:
        """RX specific configuration of internall PLL config.

        This method will update the config struct to include
        the RX clocking constraints
        """
        adc_clk = self.datapath_decimation * self.sample_clock
        self.config["l"] = self.model.Var(integer=True, lb=1, ub=4, value=1)
        self.config["adc_clk"] = self.model.Const(adc_clk)
        self.config["converter_clk"] = self.model.Intermediate(
            self.config["adc_clk"] * self.config["l"]
        )


class ad9081_tx(ad9081_core, converter):
    """AD9081 Transmit model."""

    _model_type = "dac"

    def _converter_clock_config(self) -> None:
        """TX specific configuration of internall PLL config.

        This method will update the config struct to include
        the TX clocking constraints
        """
        dac_clk = self.datapath_interpolation * self.sample_clock
        self.config["dac_clk"] = self.model.Const(dac_clk)
        self.config["converter_clk"] = self.model.Intermediate(self.config["dac_clk"])


class ad9081(ad9081_core):
    """AD9081 combined transmit and receive model."""

    multiframe_clock = None

    def __init__(self, model: Union[GEKKO, CpoModel] = None) -> None:
        """Initialize AD9081 clocking model for TX and RX.

        This is a common class used to handle TX and RX constraints
        together.

        Args:
            model (GEKKO,CpoModel): Solver model
        """
        self.adc = ad9081_rx(model)
        self.dac = ad9081_tx(model)
        self.model = model

    def _get_converters(self) -> List[Union[ad9081_rx, ad9081_tx]]:
        return [self.adc, self.dac]

    def get_required_clock_names(self) -> List[str]:
        """Get list of strings of names of requested clocks.

        This list of names is for the clocks defined by get_required_clocks

        Returns:
            List[str]: List of strings of clock names in order
        """
        clk = "ad9081_dac_clock" if self.adc.use_direct_clocking else "ad9081_pll_ref"
        return [clk, "ad9081_adc_sysref", "ad9081_dac_sysref"]

    def _converter_clock_config(self) -> None:
        adc_clk = self.adc.datapath_decimation * self.adc.sample_clock
        dac_clk = self.dac.datapath_interpolation * self.dac.sample_clock
        l = dac_clk / adc_clk
        if l not in self.adc.l_possible:
            raise Exception(
                f"ADC clock must be DAC clock/L where L={self.adc.l_possible}"
            )

        self.config["dac_clk"] = self.model.Const(dac_clk)
        self.config["adc_clk"] = self.model.Const(adc_clk)
        self.config["converter_clk"] = self.model.Intermediate(self.config["dac_clk"])

    def get_required_clocks(self) -> List:
        """Generate list required clocks.

        For AD9081 this will contain [converter clock, sysref requirement SOS]

        Returns:
            List: List of solver variables, equations, and constants

        Raises:
            Exception: If direct clocking is used. Not yet implemented
        """
        # SYSREF
        self.config = {}
        self.config["adc_lmfc_divisor_sysref"] = self.model.Var(
            integer=True, lb=1, ub=20, value=19
        )
        self.config["dac_lmfc_divisor_sysref"] = self.model.Var(
            integer=True, lb=1, ub=20, value=19
        )
        self.config["sysref_adc"] = self.model.Intermediate(
            self.adc.multiframe_clock
            / (
                self.config["adc_lmfc_divisor_sysref"]
                * self.config["adc_lmfc_divisor_sysref"]
            )
        )
        self.config["sysref_dac"] = self.model.Intermediate(
            self.dac.multiframe_clock
            / (
                self.config["dac_lmfc_divisor_sysref"]
                * self.config["dac_lmfc_divisor_sysref"]
            )
        )

        # Device Clocking
        if self.use_direct_clocking:
            raise Exception("Not implemented yet")
            # adc_clk = self.sample_clock * self.datapath_decimation
        else:
            clk = self._pll_config()

        # Objectives
        # self.model.Obj(self.config["sysref"])  # This breaks many searches
        # self.model.Obj(-1*self.config["lmfc_divisor_sysref"])

        return [clk, self.config["sysref_adc"], self.config["sysref_dac"]]
