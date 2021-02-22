from abc import ABCMeta, abstractmethod

from adijif.jesd import jesd
from gekko import GEKKO
from docplex.cp.model import CpoModel

from adijif.gekko_trans import gekko_translation


class converter(jesd, gekko_translation, metaclass=ABCMeta):
    @property
    @abstractmethod
    def name(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def direct_clocking(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def available_jesd_modes(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def K_possible(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def L_possible(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def M_possible(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def N_possible(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def Np_possible(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def F_possible(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def device_clock_available(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def device_clock_ranges(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def get_required_clocks(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def get_required_clock_names(self):
        raise NotImplementedError

    def _get_converters(self):
        return self

    def __str__(self):
        return f"{self.name} data converter model"

    def __init__(self, model=None, solver=None):
        if solver:
            self.solver = solver
        if self.solver == "gekko":
            if model:
                assert isinstance(
                    model, GEKKO
                ), "Input model must be of type gekko.GEKKO"
            else:
                model = GEKKO(remote=False)
        elif self.solver == "CPLEX":
            if model:
                assert isinstance(
                    model, CpoModel
                ), "Input model must be of type docplex.cp.model.CpoModel"
            else:
                model = CpoModel()
        else:
            raise Exception(f"Unknown solver {self.solver}")
        self.model = model

    # available_jesd_modes = ["jesd204b"]
    # K_possible = [4, 8, 12, 16, 20, 24, 28, 32]
    # L_possible = [1, 2, 4]
    # M_possible = [1, 2, 4, 8]
    # N_possible = range(7, 16)
    # Np_possible = [8, 16]
    # F_possible = [1, 2, 4, 8, 16]
    # CS_possible = [0, 1, 2, 3]
    # CF_possible = [0]
    # # S_possible = [1]  # Not found in DS
    # link_min = 3.125e9
    # link_max = 12.5e9
