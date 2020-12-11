from abc import ABCMeta, abstractmethod


class clock(metaclass=ABCMeta):
    @property
    @abstractmethod
    def find_dividers(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def list_possible_references(self):
        raise NotImplementedError
