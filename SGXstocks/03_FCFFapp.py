from tkinter import *
import tkinter
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

fcff_df = pd.read_excel('SGXstocks/FCFF_analysis_filtered.xlsx', index_col=[0])
price_hist_df = pd.read_csv('SGXstocks/PriceHistory/SGX-priceHist.csv', index_col=[0])
sgx_df = pd.read_csv('SGXstocks/StocksTable/myData.csv', index_col=[1])


class StonksApp:
    def __init__(self, master):
        self.master = master
        master.title("StonkApp")

        #set up frame with charts and stats
        self.idx = 0
        self.update_main_frame()

        #set up frame for app buttons
        self.buttons()

    #function to plot graph for df given to function 
    def plot_chart(self, row, column, df, df2=[], title="", xlabel="", ylabel="", columnspan=2):
        figure = plt.Figure(figsize=(6,5), dpi=70)
        ax = figure.add_subplot(111)
        line_graph = FigureCanvasTkAgg(figure, self.main_frame)
        line_graph.get_tk_widget().grid(row=row, column=column, columnspan=columnspan)

        df.plot(kind='line', legend=True, ax=ax)
        df2.plot(kind='line', legend=True, ax=ax)

        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

    #function to populate main frame
    def update_main_frame(self):
        self.main_frame = Frame(self.master)
        self.main_frame.grid(row=0, column=0)
        current_stock = fcff_df.index[self.idx]

        #plot graph of price history
        self.plot_chart(0, 0, df=price_hist_df[current_stock], df2=price_hist_df["A17U.SI"], title="Price History", xlabel="Date", ylabel="Price(SGD)")
        
        #show name of stock
        trading_code = current_stock.replace(".SI", "")
        self.trading_name = sgx_df.loc[trading_code, "Trading Name"]
        self.trading_name_label = Label(self.main_frame, text= f"Name: \n{self.trading_name}", font='Helvetica 10')
        self.trading_name_label.grid(row=1, column=0)

        #show sector of stock
        self.sector = sgx_df.loc[trading_code, "Sector"]    
        self.sector_label = Label(self.main_frame, text= f"Sector: \n{self.sector}", font='Helvetica 10')
        self.sector_label.grid(row=1, column=1)

        #show wacc of stock
        self.wacc = fcff_df.loc[current_stock, "WACC"]      #extract wacc of stock
        self.wacc_label = Label(self.main_frame, text= f"WACC: \n{self.wacc}", font='Helvetica 10')
        self.wacc_label.grid(row=2, column=0)

        #show fcf of stock
        self.fcff = fcff_df.loc[current_stock, "FCFF"]
        self.shares_out = fcff_df.loc[current_stock, "Shares outstanding"]
        self.fcf = self.fcff/self.shares_out
        self.fcf_label = Label(self.main_frame, text=f"FCF: \n{self.fcf}", font="Helvetica 10")
        self.fcf_label.grid(row=2, column=1)

        #show fair value stat
        self.fair_value = fcff_df.loc[current_stock, "Fair value"]   
        self.fair_value_label = Label(self.main_frame, text= f"Fair value: \n{self.fair_value}", font='Helvetica 10')
        self.fair_value_label.grid(row=3, column=0)

        #show percentage undervalued stat
        self.percentage_undervalued = fcff_df.loc[current_stock, "Percentage undervalued"]   
        self.percentage_undervalued_label = Label(self.main_frame, text= f"Percentage undervalued: \n{self.percentage_undervalued}", font='Helvetica 10')
        self.percentage_undervalued_label.grid(row=3, column=1)


    #function to populate button frame
    def buttons(self):
        self.button_frame = tkinter.Frame(self.master)

        self.back_button = Button(self.button_frame, text="Back", command=lambda: self.next(self.idx - 1))
        self.back_button.grid(row=0, column=0, pady="10", padx="10")

        self.next_button = Button(self.button_frame, text="Next", command=lambda: self.next(self.idx + 1))
        self.next_button.grid(row=0, column=1)

        self.like_button = Button(self.button_frame, text="Like")
        self.like_button.grid(row=1, column=0, pady="5", padx="10")

        self.watchlist_button = Button(self.button_frame, text="Watchlist")
        self.watchlist_button.grid(row=1, column=1, pady="5", padx="10")

        self.button_frame.grid(row=1, column=0)

    ##### function to make buttons interactable #####

    #function for next and back buttons
    def next(self, idx):
        #update main frame
        self.idx = idx
        self.update_main_frame()



        



root = Tk()
StonksApp(root)
root.mainloop()
