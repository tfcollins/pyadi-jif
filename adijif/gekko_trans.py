from abc import ABCMeta, abstractmethod

import gekko
import numpy as np
from docplex.cp.model import *


class gekko_translation(metaclass=ABCMeta):
    """ Gekko translation function """

    # @property
    # @abstractmethod
    # def model(self):
    #     raise NotImplementedError
    mode = None

    solver = "gekko"  # "CPLEX"

    def _add_equation(self, eqs):

        if not isinstance(eqs, list):
            eqs = [eqs]

        if self.solver == "gekko":
            self.model.Equations(eqs)
        elif self.solver == "CPLEX":
            for eq in eqs:
                self.model.add_constraint(eq)
        else:
            raise Exception(f"Unknown solver {self.solver}")

    def _get_val(self, value):

        if type(value) in [
            gekko.gk_variable.GKVariable,
            gekko.gk_operators.GK_Intermediate,
        ]:
            return value.value[0]
        elif type(value) is gekko.gk_operators.GK_Operators:
            return value.value
        else:
            return value

    def _check_in_range(self, value, possible, varname):
        if not isinstance(value, list):
            value = [value]
        for v in value:
            if v not in possible:
                raise Exception(f"{v} invalid for {varname}. Only {possible} possible")

    def _convert_input(self, val, name):
        if self.solver == "gekko":
            return self._convert_input_gekko(val, name)
        elif self.solver == "CPLEX":
            return self._convert_input_cplex(val, name)
        else:
            raise Exception(f"Unknown solver {self.solver}")

    def _convert_input_gekko(self, val, name):
        if isinstance(val, list) and len(val) > 1:
            return self._convert_list(val, name)
        else:
            return self.model.Const(value=val, name=name + "_Const")

    def _convert_input_cplex(self, val, name):
        return integer_var(domain=val, name=name)

    def _convert_list(self, val, name):

        # Check if contiguous by simply stride
        delta = val[0] - val[1]
        for i in range(len(val) - 1):
            if val[i] - val[i + 1] is not delta:
                # Must use SOS2
                print(val[i] - val[i + 1], delta)
                return self._convert_list2sos(val, name)

        if np.abs(delta) == 1:  # Easy mode
            print(np.min(val), np.max(val))
            return self.model.Var(
                integer=True,
                lb=np.min(val),
                ub=np.max(val),
                value=np.min(val),
                name=name + "_Var",
            )

        else:
            # SOS practical in small cases
            if len(val) < 6:
                print("SOS pract")
                return self._convert_list2sos(val, name)
            # Since stride is not zero the best is to use a scale
            # factor and intermediate for best solving performance

            # Need to fit-> (Array+B)*C+D == org_arrar
            # 1,3,5 -> ([1,2,3]-1) * 2 + 1
            # 3,6,9 -> [1,2,3]*3
            # 2,4,6 -> [1,2,3]*2

            raise Exception("NOT COMPLETE")

            val = np.array(val)
            l = len(val)
            Array = np.array(range(1, l + 1))
            for B in range(0, l):
                for C in range(1, l):
                    for D in range(0, l):
                        if val == (Array + B) * C + D:
                            break
            array = self.model.Var(
                integer=True, lb=1, ub=4, value=1, name=name + "_Var"
            )

    def _convert_list2sos(self, val, name):
        print("SOS")
        sos = self.model.sos1(val)
        # sos.NAME = name + "_SOS1"
        return sos

    def _convert_back(self, value):
        print(type(value))
        return value
