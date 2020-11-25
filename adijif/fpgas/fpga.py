from abc import ABCMeta, abstractmethod

class fpga(metaclass=ABCMeta):

    @property
    @abstractmethod
    def determine_cpll(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def determine_qpll(self):
        raise NotImplementedError
