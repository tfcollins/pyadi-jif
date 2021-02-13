from abc import ABCMeta, abstractmethod

from gekko import GEKKO

from adijif.gekko_trans import gekko_translation


class clock(gekko_translation, metaclass=ABCMeta):
    @property
    @abstractmethod
    def find_dividers(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def list_possible_references(self):
        raise NotImplementedError

    def solve(self):
        self.model.options.SOLVER = 1  # APOPT solver
        self.model.solve(disp=False)

    def __init__(self, model=None):
        if model:
            assert isinstance(model, GEKKO), "Input model must be of type gekko.GEKKO"
        else:
            model = GEKKO()
        self.model = model
