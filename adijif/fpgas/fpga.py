from abc import ABCMeta, abstractmethod

from gekko import GEKKO


class fpga(metaclass=ABCMeta):
    @property
    @abstractmethod
    def determine_cpll(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def determine_qpll(self):
        raise NotImplementedError

    def __init__(self, model=None):
        if model:
            assert isinstance(model, GEKKO), "Input model must be of type gekko.GEKKO"
        else:
            model = GEKKO()
        self.model = model
