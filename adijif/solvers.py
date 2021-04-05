"""Common solver API management layer."""
try:
    from docplex.cp.expression import CpoExpr  # type: ignore
    from docplex.cp.expression import CpoFunctionCall, CpoIntVar
    from docplex.cp.model import binary_var  # type: ignore
    from docplex.cp.model import CpoModel, integer_var  # type: ignore
    from docplex.cp.solution import CpoSolveResult  # type: ignore

    cplex_solver = True
except ImportError:
    cplex_solver = False
    CpoExpr = None
    CpoFunctionCall = None
    binary_var = None
    integer_var = None

try:
    from gekko import GEKKO  # type: ignore
    from gekko.gk_operators import GK_Intermediate  # type: ignore
    from gekko.gk_operators import GK_Operators  # type: ignore
    from gekko.gk_variable import GKVariable  # type: ignore

    gekko_solver = True
except ImportError:
    gekko_solver = False
    GEKKO = None
    GK_Intermediate = None
    GK_Operators = None
    GKVariable = None
