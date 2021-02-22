from abc import ABCMeta, abstractmethod

from gekko import GEKKO
from docplex.cp.model import CpoModel

from adijif.gekko_trans import gekko_translation


class fpga(gekko_translation, metaclass=ABCMeta):

    solver = "gekko"  # "CPLEX"

    @property
    @abstractmethod
    def determine_cpll(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def determine_qpll(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def get_config(self):
        raise NotImplementedError

    def __init__(self, model=None, solver=None):
        if solver:
            self.solver = solver
        if self.solver == "gekko":
            if model:
                assert isinstance(
                    model, GEKKO
                ), "Input model must be of type gekko.GEKKO"
            else:
                model = GEKKO()
        elif self.solver == "CPLEX":
            assert isinstance(
                model, CpoModel
            ), "Input model must be of type docplex.cp.model.CpoModel"
        else:
            raise Exception(f"Unknown solver {self.solver}")
        self.model = model
