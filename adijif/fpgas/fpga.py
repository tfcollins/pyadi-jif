from abc import ABCMeta, abstractmethod

from gekko import GEKKO
from docplex.cp.model import CpoModel

from adijif.gekko_trans import gekko_translation
from adijif.common import core


class fpga(core, gekko_translation, metaclass=ABCMeta):
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
