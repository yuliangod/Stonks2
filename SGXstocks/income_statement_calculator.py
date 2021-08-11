from tkinter import *
from matplotlib.pyplot import text 
import pandas as pd
import re

class income_statement_calculator():
    def __init__(self, master, stock):
        self.master = master
        master.title("Calculator")
        master.geometry("500x750")

        self.calculator_screen = Text(root, height=5)
        self.calculator_screen.pack()
        #self.calculator_screen.insert(END,"abc")

        self.stock = stock

        self.update_statement_frame()
        
    #income statement selection page
    def update_statement_frame(self):
        self.statement_frame = Frame(self.master)
        self.statement_frame.pack()

        self.IS_button = Button(self.statement_frame, text="Income statement", command=lambda:self.open_statement(self.stock, "IS", 3))
        self.IS_button.pack(pady=5)
    
        self.BS_button = Button(self.statement_frame, text="Balance sheet", command=lambda:self.open_statement(self.stock, "BS", 2))
        self.BS_button.pack()

        self.CF_button = Button(self.statement_frame, text="Cash flows", command=lambda:self.open_statement(self.stock, "CF", 2))
        self.CF_button.pack(pady=5)

    #function for button to open income statements
    def open_statement(self, stock, statement, slice, column_width=2):
        self.statement = statement
        self.statement_df = pd.read_csv(f"SGXstocks/Database/{stock}/{statement}.csv", index_col=[0]).fillna(0)
        self.statement_index = self.statement_df.index[slice:]

        self.stats_frame= Frame(self.master)
        self.stats_frame.pack()

        self.statement_frame.destroy()

        #button to get back to income statements_frame
        self.back_statements_button = Button(self.stats_frame, text="<<<Back", command=lambda:self.back_statements(self.stats_frame))
        self.back_statements_button.grid(row=0, column=0, pady=10)

        #buttons of stats in statement
        for i in range(len(self.statement_index)):
            b = Button(self.stats_frame, text=self.statement_index[i], command=lambda i=i: self.stats_button(self.statement_index[i]))
            b.grid(row=i//column_width + 1, column=i%column_width, pady=1)

    #function to get back to income statement selection page
    def back_statements(self, frame, clear_screen=False):
        frame.destroy()
        self.update_statement_frame()

        if clear_screen == True:
            self.calculator_screen.delete('1.0', END)

    
    #function to choose stat in income statement
    def stats_button(self, stat):
        self.stat = stat.replace(" ","_")

        self.years_frame= Frame(self.master)
        self.years_frame.pack()

        self.stats_frame.destroy()

        #button to get back to statements_frame
        self.back_statements_button = Button(self.years_frame, text="<<<Back", command=lambda:self.back_statements(self.years_frame))
        self.back_statements_button.grid(row=0, column=0)

        #label to show current stat
        stat_label = Label(self.years_frame, text=stat)
        stat_label.grid(row=1, columnspan=4)


        self.years_list = self.statement_df.columns
        #buttons of years
        for i in range(len(self.years_list)):
            b = Button(self.years_frame, text=self.years_list[i], command=lambda i=i: self.years_button(self.years_list[i]))
            b.grid(row=2, column=i, pady=5)

    #function to choose year of the stat 
    def years_button(self, year):
        self.calculator_screen.insert(END, f"[{self.statement}]{self.stat}({year}) ")

        #bring user to frame with arithmetic operations
        self.years_frame.destroy()

        self.arith_frame = Frame(self.master)
        self.arith_frame.pack()

        self.arith_list = ["+", "-", "/", "*"]
        for i in range(len(self.arith_list)):
            b = Button(self.arith_frame, text=self.arith_list[i], command=lambda i=i:self.arith_button(self.arith_list[i]))
            b.grid(row=0, column=i)

        #equal button
        self.equal_button = Button(self.arith_frame, text="=", command=self.equal)
        self.equal_button.grid(row=0, column=len(self.arith_list)+1)

    #bring user back to income statements page to select next stat
    def arith_button(self, operator):
        self.calculator_screen.insert(END, f"{operator} ")
        self.back_statements(self.arith_frame)

    #grab string from text widget and perform calculations based on whats on the screen
    def equal(self):
        input = self.calculator_screen.get("1.0",END)
        input_list = input.split()

        self.code_list = []  #empty list to store stats to write code
        #get even numbered index to substitute stat for value
        for i in range(len(input_list)):
            if i%2 == 0:
                year_regex = re.search(r"\[(\w+)\](\D+)\((\d+)\)", input_list[i])
                statement = year_regex.group(1)
                statement_df = pd.read_csv(f"SGXstocks/Database/{self.stock}/{statement}.csv", index_col=[0]).fillna(0)

                stat = year_regex.group(2).replace("_", " ")
                year = year_regex.group(3)
                stat_value = statement_df.loc[stat, year]

                self.code_list.append([statement, stat, year])

                input_list[i] = stat_value
            else: 
                self.code_list.append(input_list[i])

        input_string = "".join(input_list)
        final_value = eval(input_string)

        #display final_value on screen and bring user to a page to get code
        self.calculator_screen.insert(END, f"= {final_value}")

        self.arith_frame.destroy()

        """ buttons frame """
        get_code_frame = Frame(self.master)
        get_code_frame.pack()

        #back_button
        self.back_statements_button = Button(get_code_frame, text="<<<Back", command=lambda:self.back_statements(get_code_frame, clear_screen=True))
        self.back_statements_button.pack()

        #get code button
        get_code_button = Button(get_code_frame, text="Get code", command=self.get_code)
        get_code_button.pack(pady=10)

    #function for get code button to open new window with code to copy paste
    def get_code(self):
        self.get_code_window = Toplevel(self.master)
        self.get_code_window.geometry("300x300")
        self.get_code_window.title("Watchlist")

        code=[]

        for i in range(len(self.code_list)):
            if i%2 == 0:
                statement, stat, year = self.code_list[i]
                code.append(f'{statement}_df.loc["{stat}", "{year}"]')
            else:
                code.append(self.code_list[i])
                

        code = " ".join(code)
        code_label = Text(self.get_code_window, padx=5, pady=5)
        code_label.insert(END, code)
        code_label.pack()

    def back_code(self):
        pass

root = Tk()
income_statement_calculator(root, "TS0U.SI")
root.mainloop()