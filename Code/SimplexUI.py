from tkinter import Tk, Frame, Label, Button, Entry, END, Spinbox, StringVar, Canvas, Scrollbar
from SimplexAlgorithm import Simplex, TableThingRow, SimplexTerminalUI, ObjectiveRow
from fractions import Fraction

class LinkedEntry:
    def __init__(self, parent):
        self.parent = parent
        self.entry_box = Entry(self.parent, borderwidth=1, relief="solid")
        self.variable_show = Entry(self.parent, state="readonly", borderwidth=1, relief="solid")
        self.entry_box.bind('<KeyRelease>', self.updateLabel)

    def get(self):
        return self.entry_box.get()

    def updateLabel(self, event):
        text = self.get()
        self.variable_show.config(state="normal")
        self.variable_show.delete(0, END)
        self.variable_show.insert(0, text)
        self.variable_show.config(state="readonly")

    def getEntry(self):
        return self.entry_box

    def getLabelEntry(self):
        return self.variable_show

class InitialTableThingEntry(Frame):
    def __init__(self, master, normal_vars: int, slack_vars: int):
        super().__init__(master)
        for column in range(slack_vars + 2): self.columnconfigure(column, weight=1)
        for row in range(normal_vars + slack_vars + 2): self.columnconfigure(row, weight=1)
        self.normal_vars_names_entries = []
        self.slack_vars_names_entries = []
        self.values_entries = []
        self.objective_var_entry = Entry(self, borderwidth=1, relief="solid")
        self.setSetUpHeadings(normal_vars, slack_vars)
        self.setUpValEntries(normal_vars, slack_vars)


    def setSetUpHeadings(self, normal_vars: int, slack_vars: int):
        for var_number in range(1, normal_vars + 1):
            current_var_entry = Entry(self, borderwidth=1, relief="solid")
            self.normal_vars_names_entries.append(current_var_entry)
            current_var_entry.grid(row=0, column=var_number, sticky="nsew")
        for var_number in range(1, slack_vars+1):
            current_var_entry = LinkedEntry(self)
            self.slack_vars_names_entries.append(current_var_entry)
            current_var_entry.getEntry().grid(row=var_number, column=0, sticky="nsew")
            current_var_entry.getLabelEntry().grid(row=0, column=var_number + normal_vars, sticky="nsew")
        self.objective_var_entry.grid(row=slack_vars+1, column=0, sticky="nsew")
        Label(self, text="Value", borderwidth=1, relief="solid", width=20).grid(row=0, column=normal_vars + slack_vars + 1, sticky="nsew")

    def setUpValEntries(self, normal_vars: int, slack_vars: int):
        rows = []
        for row_number in range(1, slack_vars+2):
            current_row = []
            for normal_var in range(1, normal_vars + 1):
                current_entry = Entry(self)
                current_entry.grid(row=row_number, column=normal_var, sticky="nsew")
                current_row.append(current_entry)
            for slack_var in range(0, slack_vars):
                current_entry = Entry(self)
                current_row.append(current_entry)
                current_entry.insert(0, str(int(row_number-1 == slack_var)))
                current_entry.config(state="readonly")
                current_entry.grid(row=row_number, column=slack_var+normal_vars+1, sticky="nsew")
            value_entry = Entry(self)
            current_row.append(value_entry)
            value_entry.grid(row=row_number, column=normal_vars+slack_vars+1, sticky="nsew")
            rows.append(current_row)
        self.values_entries = rows

    def tryReadAsTable(self) -> tuple[bool, Simplex | None]:
        try:
            table = self.readEntry()
            return True, table
        except ValueError:
            return False, None

    def readAsTableRows(self) -> list:
        rows = []
        for row_number in range(len(self.values_entries)):
            row = self.values_entries[row_number]
            current_dict = {}
            for variable_number in range(0, len(self.normal_vars_names_entries)):
                current_dict[self.normal_vars_names_entries[variable_number].get()] = Fraction(row[variable_number].get())
            for slack_variable_number in range(0, len(self.slack_vars_names_entries)):
                current_dict[self.slack_vars_names_entries[slack_variable_number].get()] = Fraction(row[slack_variable_number+len(self.normal_vars_names_entries)].get())
            if row_number != len(self.values_entries)-1:
                rows.append(TableThingRow(current_dict, Fraction(row[-1].get()), self.slack_vars_names_entries[row_number].get()))
            else:
                rows.append(ObjectiveRow(current_dict, Fraction(row[-1].get()), self.objective_var_entry.get()))
        return rows

    def readEntry(self):
        table_thing_rows = self.readAsTableRows()
        return SimplexTerminalUI(table_thing_rows, table_thing_rows[-1])


    def getNormalVarNames(self):
        return [var.get() for var in self.normal_vars_names_entries]

    def getSlackVarNames(self):
        return [var.get() for var in self.slack_vars_names_entries]

    def getAllVarNames(self):
        return self.getNormalVarNames() + self.getSlackVarNames()

    def checkVarsUnique(self) -> bool:
        all_vars = self.getAllVarNames()
        return len(set(all_vars)) == len(all_vars)

class ValEntry(Entry):
    def __init__(self, master, expected_value: int | Fraction):
        super().__init__(master)
        self.expected_value = expected_value
        self.correct = False # incase I want to put a correct message at the end
        self.showing_answer = False
        self.prev_entered = ""
        self.bind('<KeyRelease>', self.enterValue)

    def isCorrect(self) -> bool:
        return self.correct

    def showCorrect(self):
        self.config(bg="#c8edc5")
        # self.disable()
        self.correct = True

    def showIncorrect(self):
        self.config(bg="#f5c1c1")
        # self.enable()
        self.correct = False

    def showIncorrectBlank(self):
        self.config(bg="white")
        # self.enable()
        self.correct = False

    def showAnswer(self):
        if not self.showing_answer: self.prev_entered = self.get()
        self.delete(0, END)
        self.insert(0, str(self.expected_value))
        self.showCorrect()
        self.showing_answer = True

    def hideAnswer(self):
        self.showIncorrect()
        self.delete(0, END)
        self.insert(0, self.prev_entered)
        self.showing_answer = False
        self.enterValue(None)

    def enterValue(self, event):
        try:
            if Fraction(self.get()) == self.expected_value:
                self.showCorrect()
            else:
                self.showIncorrect()
        except:
            if (self.get() == "undefined" or self.get() == "inf") and self.expected_value == float("inf"):
                self.showCorrect()
            elif self.get() == "":
                self.showIncorrectBlank()
            else:
                self.showIncorrect()

    def enable(self):
        self.configure(state="normal")

    def disable(self):
        self.configure(state="readonly")

class TableRowWidgets:
    def __init__(self, master, table_row: TableThingRow, pivot_var: str):
        self.master = master
        self.entry_widgets = {}
        self.value_widget = None
        self.theta_value_widget = None
        self.createEntryWidgets(table_row, pivot_var)

    def createEntryWidgets(self, table_row: TableThingRow, pivot_var: str):
        for variable in table_row.getVarNames():
            self.entry_widgets[variable] = ValEntry(self.master, table_row.getVarCoef(variable))
        self.value_widget = ValEntry(self.master, table_row.getValue())
        self.theta_value_widget = ValEntry(self.master, table_row.getThetaValue(pivot_var))

    def getWidget(self, var_name: str):
        return self.entry_widgets[var_name]

    def getValueWidget(self):
        return self.value_widget

    def getThetaWidget(self):
        return self.theta_value_widget


class TableSolutionShow(Frame):
    def __init__(self, master, table: Simplex, variable_names: list):
        super().__init__(master)
        for column in range(0, len(variable_names)+4): self.columnconfigure(column, weight=1, minsize=15)
        for row in range(0, len(variable_names) + 1): self.rowconfigure(row, weight=1)
        self.table_thing: Simplex = table
        self.variable_names = variable_names
        self.is_pivot, self.pivot_var = self.table_thing.getPivotColName()
        self.entries = []
        self.showTable()

    def showTable(self):
        col_headings = self.variable_names + ["Value"] + ["Theta value"]*int(not self.is_pivot) + ["Working...?"]
        for col_number in range(len(col_headings)):
            Label(self, text=col_headings[col_number], borderwidth=1, relief="solid").grid(row=0, column=col_number + 1, sticky="nsew")
        for row_number in range(len(self.table_thing)):
            row: TableThingRow = self.table_thing[row_number]
            row_widgets = TableRowWidgets(self, row, self.pivot_var)
            Label(self, text=row.getVarName(), borderwidth=1, relief="solid").grid(row=row_number+1, column=0, sticky="nsew")
            for col_number in range(len(self.variable_names)):
                var = self.variable_names[col_number]
                entry = row_widgets.getWidget(var)
                entry.grid(row=row_number+1, column=col_number+1, sticky="nsew")
                self.entries.append(entry)
            additional_widgets = [row_widgets.getValueWidget()] + [row_widgets.getThetaWidget() if type(row) != ObjectiveRow else None]*int(not self.is_pivot) + [Entry(self)]
            for entry_number in range(len(additional_widgets)):
                entry = additional_widgets[entry_number]
                if entry is not None:
                    if type(entry) == ValEntry: self.entries.append(entry)
                    entry.grid(row=row_number+1, column=entry_number+len(self.variable_names)+1, sticky="nsew") # todo ??

    def showAnswer(self):
        for entry in self.entries:
            entry.showAnswer()

    def hideAnswer(self):
        for entry in self.entries:
            entry.hideAnswer()

    def isFinished(self):
        for entry in self.entries:
            if not entry.isCorrect():
                return False
        return True

class ShowAnswerButton(Button):
    def __init__(self, master, show_answer_func, hide_answer_func, showing_answer=False):
        super().__init__(master, command=self.nextState)
        self.showing_answer = showing_answer
        self.text_options = ["Show answer!", "Hide answer"]
        self.showText()
        self.show_answer_func = show_answer_func
        self.hide_answer_func = hide_answer_func

    def showText(self):
        self.config(text=self.text_options[int(self.showing_answer)])

    def nextState(self):
        if self.showing_answer:
            self.hide_answer_func()
        else:
            self.show_answer_func()
        self.showing_answer = not self.showing_answer
        self.showText()

    def changeCommands(self, hide_answer_func, show_answer_func):
        self.hide_answer_func = hide_answer_func
        self.show_answer_func = show_answer_func

    def reset(self):
        self.showing_answer = False
        self.showText()



class SolutionTables(Frame):
    def __init__(self, master, table: Simplex, variable_names: list):
        super().__init__(master)
        for column in range(0, 1): self.columnconfigure(column, weight=1)
        for row in range(0, len(variable_names)): self.rowconfigure(row, weight=1)
        self.table: Simplex = table
        self.variable_names: list = variable_names
        # set up UI:
        Label(self, text="Enter the numbers in the tables or just look at the answer (copy the initial table first):")
        # self.table_widgets = []
        self.tables_frame = Frame(self)
        self.tables_frame.columnconfigure(0, weight=1)
        self.current_table_widget = TableSolutionShow(self.tables_frame, self.table, self.variable_names)
        self.current_table_widget.pack(padx=5, pady=5, expand=True, fill="both")
        self.tables_frame.grid(row=0, column=0, sticky="nsew")
        self.show_answer_button = ShowAnswerButton(self, self.showAnswer, self.hideAnswer)
        self.show_answer_button.grid(row=1, column=0, sticky="ew")
        self.feedback_label = Label(self, fg="red")
        self.feedback_label.grid(row=3, column=0, sticky="nsew")
        self.next_button = Button(self, text="Show next table", command=self.nextTable)
        self.next_button.grid(row=2, column=0, sticky="ew")

    def setUpNextTable(self):
        self.current_table_widget = TableSolutionShow(self.tables_frame, self.table, self.variable_names)
        self.hideAnswer()
        self.current_table_widget.pack(padx=5, pady=5, expand=True, fill="both")
        self.show_answer_button.reset()

    def finished(self):
        self.feedback_label.config(text="Finished!!", fg="green")
        self.next_button.destroy()
        self.show_answer_button.destroy()

    def nextTable(self):
        if self.current_table_widget.isFinished():
            self.hideNotFinishedFeedback()
            finished = self.table.performIteration()
            if finished:
                self.finished()
            else:
                self.setUpNextTable()
        else:
            self.showNotFinishedFeedback()

    def showAnswer(self):
        self.current_table_widget.showAnswer()

    def hideAnswer(self):
        self.current_table_widget.hideAnswer()

    def showNotFinishedFeedback(self):
        self.feedback_label.config(text="Finish previous table first!")

    def hideNotFinishedFeedback(self):
        self.feedback_label.config(text="")

class TableDimensionsEntry(Frame):
    def __init__(self, master):
        super().__init__(master)
        for column in range(0, 3): self.columnconfigure(column, weight=1)
        for row in range(0, 3): self.rowconfigure(row, weight=1)
        Label(self, text="Enter table info", font=("Arial", 16, "bold")).grid(row=0, column=0, sticky="nsew", columnspan=2)
        Label(self, text="Number of variables (not including slack):").grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.vars_sb = Spinbox(self, from_=1, to=15, wrap=True, textvariable=StringVar(), width=2, state="readonly")
        self.vars_sb.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        Label(self, text="Number of constraints (not including objective):").grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        self.constraints_sb = Spinbox(self, from_=1, to=20, wrap=True, textvariable=StringVar(), width=2, state="readonly")
        self.constraints_sb.grid(row=2, column=1, sticky="nsew", padx=10, pady=10)

    def getNoOfVars(self):
        return int(self.vars_sb.get())

    def getNoOfConstraints(self):
        return int(self.constraints_sb.get())

class InitialInfoEntry(Frame):
    def __init__(self, master, table_submit_func):
        super().__init__(master)
        for column in range(0, 1): self.columnconfigure(column, weight=1)
        for row in range(0, 3): self.rowconfigure(row, weight=1)
        self.submit_function = table_submit_func
        self.current_widget: TableDimensionsEntry | InitialTableThingEntry = TableDimensionsEntry(self)
        self.current_widget.grid(row=0, column=0, sticky="nsew")
        self.states = {"DIMENSION": self.submitDimensions, "TABLE": self.submitTableThing, "ENTERED": lambda: None}
        self.current_state = "DIMENSION"
        self.submit_button = Button(self, text="Ok", command=self.next)
        self.submit_button.grid(row=1, column=0, sticky="ew")
        self.feedback_label = Label(self, fg="red")
        self.feedback_label.grid(row=2, column=0, sticky="ew")

    def submitDimensions(self):
        vars_no = self.current_widget.getNoOfVars()
        constraints_no = self.current_widget.getNoOfConstraints()
        self.current_widget.destroy()
        self.current_widget = InitialTableThingEntry(self, vars_no, constraints_no)
        self.current_widget.grid(row=0, column=0, sticky="nsew")
        self.current_state = "TABLE"

    def submitTableThing(self):
        successful, table = self.current_widget.tryReadAsTable()
        if not successful:
            self.showInvalidError()
        elif not self.current_widget.checkVarsUnique():
            self.showNotUniqueVarsError()
        else:
            variables = self.current_widget.getAllVarNames()
            self.showCompleteInitialEntry()
            self.submit_function(table, variables)


    def showCompleteInitialEntry(self):
        self.submit_button.destroy()
        self.clearErrors()

    def next(self):
        self.states[self.current_state]()

    def showInvalidError(self):
        self.feedback_label.config(text="Some / all values entered into the table are invalid (please fill all).")

    def showNotUniqueVarsError(self):
        self.feedback_label.config(text="Variables must be unique.")

    def clearErrors(self):
        self.feedback_label.config(text="")


class Main(Frame):
    def __init__(self):
        super().__init__()
        for column in range(0, 1): self.columnconfigure(column, weight=1)
        # for row in range(0, 3): self.rowconfigure(row, weight=1)
        Button(self, text="Reset", command=self.reset).grid(row=0, column=0, padx=5, pady=5, sticky="new")
        self.initial_table_entry = InitialInfoEntry(self, self.submitInitialTable)
        self.initial_table_entry.grid(row=1, column=0, padx=5, pady=5, sticky="new")
        self.entry_tables = Frame()
        # self.scroll = Frame()
        ## configure scrollbar

    def reset(self):
        self.initial_table_entry.destroy()
        self.entry_tables.destroy()
        self.initial_table_entry = InitialInfoEntry(self, self.submitInitialTable)
        self.initial_table_entry.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.entry_tables = Frame()

    def submitInitialTable(self, table, variables):
        # self.scroll = Scrollbar(self)
        # self.scroll.grid(row=2, column=1, sticky="ns")
        self.entry_tables = SolutionTables(self, table, variables)
        # self.scroll.config(command=self.entry_tables.yview)
        self.entry_tables.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")


class MainScrollable(Tk):
    def __init__(self):
        super().__init__()
        for col in range(0, 1): self.columnconfigure(col, weight=1)
        for row in range(0, 1): self.rowconfigure(row, weight=1)
        self.geometry("800x500")
        self.resizable(True, True)
        self.title("Simplex")
        self.main_canvas = Canvas(self)
        self.main_canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar = Scrollbar(self)
        scrollbar.grid(row=0, column=1, sticky="ns")
        scrollbar.config(command=self.main_canvas.yview)
        self.main_canvas.configure(yscrollcommand=scrollbar.set)
        self.main_frame = Main()
        self.inner_canvas = self.main_canvas.create_window((0, 0), window=self.main_frame, anchor="nw")
        self.main_frame.bind("<Configure>", lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all")))
        self.main_canvas.bind("<Configure>", self.resizeCanvas)

    def resizeCanvas(self, event):
        self.main_canvas.itemconfig(self.inner_canvas, width=event.width)
        # self.rowconfigure(0, weight=1)
        # self.columnconfigure(0, weight=1)



# add a scrollbar
# complete reset
# make expandable

MainScrollable().mainloop()

"""
a = Tk()
b = InitialTableThingEntry(a, 2, 2)
b.pack()

def solve():
    successful, table = b.tryReadAsTable()
    if successful: table.performAllIterations()

Button(a, text="solve", command=solve).pack()

a.mainloop()
"""
# todo fix problem that occuring with example bc of negative and *0 for theta value text but at wrong time

# if anyone reads this, know I am aware of how messy and inefficient this whole code is as I rushed some of it but it works
