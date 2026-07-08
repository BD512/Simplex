from fractions import Fraction

class TableThingRow:
    def __init__(self, variables: dict[str: int | Fraction],  value: Fraction | int, row_var_name: str):
        self.variables = variables # to include slack variable_names
        self.value = value
        self.row_var_name = row_var_name

    def getValue(self):
        return self.value

    def getVarNames(self) -> set[str]:
        return set(self.variables.keys())

    def getVarName(self):
        return self.row_var_name

    def getThetaValue(self, pivot_var_name: str) -> Fraction | float:
        try:
            return Fraction(self.value, self.variables[pivot_var_name])
        except KeyError:
            raise Exception("There is no variable named " + pivot_var_name)
        except ZeroDivisionError:
            return float("inf")

    def getVarCoef(self, var_name: str) -> Fraction | float:
        return self.variables[var_name]

    def addVar(self, var_name):
        if var_name not in self.variables.keys():
            self.variables[var_name] = 0

    def makeCol1(self, var_name):
        factor = self.variables[var_name]
        self.row_var_name = var_name
        for var in self.variables.keys():
            self.variables[var] = Fraction(self.variables[var], factor)

    def makeVal1(self, var_name):
        factor = self.variables[var_name]
        self.value = Fraction(self.value, factor)

    def makeCol0(self, var_name, other_row):
        factor = Fraction(-self.variables[var_name], other_row.getVarCoef(var_name))
        for var in self.variables.keys():
            self.variables[var] = self.variables[var] + Fraction(other_row.getVarCoef(var)) * factor

    def makeVal0(self, var_name, other_row):
        factor = Fraction(-self.variables[var_name], other_row.getVarCoef(var_name))
        print(f"F{factor}")
        print(self.value)
        print(other_row.getValue())
        self.value = self.value + (Fraction(other_row.getValue()) * factor)


class ObjectiveRow(TableThingRow):
    def __init__(self, variables: dict, value: Fraction | int, name: str):
        TableThingRow.__init__(self, variables, value, name)

    def getThetaValue(self, pivot_var_name: str) -> Fraction | float:
        return float("inf")

    def checkForLowestVal(self) -> tuple[bool, str]: # is finished, minimum value coefficient
        min_val = min(self.variables.values())
        return min_val >= 0, [i for i in self.variables if min_val == self.variables[i]][0]

class Simplex(list):
    def __init__(self, table_rows: list[TableThingRow], objective_row: ObjectiveRow):
        super().__init__(table_rows) # I know I should have used a numpy array, it'd have been way neater and efficient and easy to scale - if I have time, I'll change it to this
        # self.table_thing_rows = table_rows # should also contain objective row
        self.objective_row = objective_row
        self.variable_names = set({})
        self.updateVars()
        # self.slack_variables = set({})

    def getVarNames(self) -> set[str]:
        return set(self.variable_names)

    def updateVars(self):
        for row in self:
            print(row.getVarNames())
            self.variable_names = set(self.variable_names.union(row.getVarNames()))
            print(self.variable_names)
            # self.slack_variables.union(row.getSlackVarNames())
        self.createZeroedCols()

    def createZeroedCols(self): # check for uncreated rows when updating rows in iteration
        for var_name in self.variable_names:
            for row in self:
                row.addVar(var_name)

    def getNextPivotRow(self, pivot_var_name: str) -> TableThingRow: # todo what if the theta values are all infinity??
        # todo what if the theta values are all negative or 0 - would this never happen
        min_theta_value = float("inf")
        pivot_row = None
        for row in self:
            current_theta_val = row.getThetaValue(pivot_var_name)
            if 0 < current_theta_val < min_theta_value:
                min_theta_value = current_theta_val
                pivot_row = row
        return pivot_row

    def getPivotColName(self) -> tuple[bool, str]:  # todo sort divide by zero for theta values
        is_finished, pivot_var_name = self.objective_row.checkForLowestVal()
        return is_finished, pivot_var_name

    def getPivot(self) -> tuple[bool, TableThingRow, str]:
        is_finished, pivot_var_name = self.objective_row.checkForLowestVal()
        pivot_row = self.getNextPivotRow(pivot_var_name)
        return is_finished, pivot_row, pivot_var_name

    def performIteration(self) -> bool: # returns whether has finished
        is_finished, pivot_row, pivot_var_name = self.getPivot()
        if is_finished:
            return True
        else:
            for row in self:
                if row != pivot_row:
                    row.makeVal0(pivot_var_name, pivot_row)
                    row.makeCol0(pivot_var_name, pivot_row)
            pivot_row.makeVal1(pivot_var_name)
            pivot_row.makeCol1(pivot_var_name)
            return False
        # new_table = np.copy(self.table_thing_rows)
        # row_index = min(self.table_thing_rows[-len(self.table_thing_rows):])

class SimplexTerminalUI(Simplex):
    def __init__(self, table_rows: list[TableThingRow], objective_row: ObjectiveRow): # change inputs to take from user
        Simplex.__init__(self, table_rows, objective_row)

    def performAllIterations(self):
        self.printTable()
        while not self.performIteration():
            self.printTable()

    def printTable(self):
        # print(self.variable_names)
        print(str(" \t|" + "".join([f"{var_name}\t\t|" for var_name in self.variable_names])))
        for row in self:
            print(str(f"{row.getVarName()} \t|" + "".join([f"{row.getVarCoef(var_name)}\t\t|" for var_name in self.variable_names])))

if __name__ == "__main__":
    objective = ObjectiveRow({"x":-3, "y":-2}, 0, "P")
    table = [TableThingRow({"x":5, "y":7, "r":1}, 70, "r"),
             TableThingRow({"x":10, "y":3, "s":1}, 60, "s"),
             objective] # change so just pass in the name of the slack variable instead as we know one per normal equation?
    a = SimplexTerminalUI(table, objective)
    a.performAllIterations()

