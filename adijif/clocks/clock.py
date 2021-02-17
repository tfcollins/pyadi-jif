"""Clock parent metaclass to maintain consistency for all clock chip."""
from abc import ABCMeta, abstractmethod
from typing import Dict, List

from gekko import GEKKO

from adijif.gekko_trans import gekko_translation


class clock(gekko_translation, metaclass=ABCMeta):
    """Parent metaclass for all clock chip classes."""

    @property
    @abstractmethod
    def find_dividers(self) -> Dict:
        """Find all possible divider settings that validate config.

        Raises:
            NotImplementedError: Method not implemented
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def list_possible_references(self) -> List[int]:
        """Determine all references that can be generated.

        Based on config list possible references that can be generated
        based on VCO and output dividers

        Raises:
            NotImplementedError: Method not implemented
        """
        raise NotImplementedError

    def solve(self) -> None:
        """Local solve method for clock model.

        Call model solver with correct arguments.
        """
        self.model.options.SOLVER = 1  # APOPT solver
        self.model.solver_options = [
            "minlp_maximum_iterations 1000",  # minlp iterations with integer solution
            "minlp_max_iter_with_int_sol 100",  # treat minlp as nlp
            "minlp_as_nlp 0",  # nlp sub-problem max iterations
            "nlp_maximum_iterations 500",  # 1 = depth first, 2 = breadth first
            "minlp_branch_method 1",  # maximum deviation from whole number
            "minlp_integer_tol 0",  # covergence tolerance (MUST BE 0 TFC)
            "minlp_gap_tol 0.1",
        ]

        self.model.solve(disp=True)

    def __init__(self, model: GEKKO = None) -> None:
        """Initalize clocking model.

        When usings the clocking models standalone, typically for
        validation flows, a solver model is created internally.
        For system level work, a shared model is passed.

        Args:
            model (GEKKO): Solver model
        """
        if model:
            assert isinstance(model, GEKKO), "Input model must be of type gekko.GEKKO"
        else:
            model = GEKKO()
        self.model = model
