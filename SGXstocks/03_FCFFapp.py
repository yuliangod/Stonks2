from tkinter import *
from tkinter import ttk
from tkinter import messagebox
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
        self.current_stock = fcff_df.index[self.idx]
        self.update_main_frame(self.current_stock)

        #set up frame for app buttons
        self.update_buttons_frame()

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
    def update_main_frame(self, stock):
        self.main_frame = Frame(self.master)
        self.main_frame.grid(row=0, column=0)

        #plot graph of revenue and operating income
        IS_df = pd.read_csv(f"SGXstocks/Database/{stock}/IS.csv", index_col=[0])
        revenue_df = IS_df.loc["Revenue"]
        revenue_df = revenue_df.astype(float)

        operating_income_df = IS_df.loc["Operating Income"] 
        operating_income_df=operating_income_df.astype(float)

        self.plot_chart(0, 0, df=revenue_df, df2=operating_income_df, title="", xlabel="Year", ylabel="")
        
        #show name of stock
        trading_code = stock.replace(".SI", "")
        self.trading_name = sgx_df.loc[trading_code, "Trading Name"]
        self.trading_name_label = Label(self.main_frame, text= f"Name: \n{self.trading_name}", font='Helvetica 10')
        self.trading_name_label.grid(row=1, column=0)

        #show sector of stock
        self.sector = sgx_df.loc[trading_code, "Sector"]    
        self.sector_label = Label(self.main_frame, text= f"Sector: \n{self.sector}", font='Helvetica 10')
        self.sector_label.grid(row=1, column=1)

        #show wacc of stock
        self.wacc = fcff_df.loc[stock, "WACC"]      #extract wacc of stock
        self.wacc_label = Label(self.main_frame, text= f"WACC: \n{self.wacc}", font='Helvetica 10')
        self.wacc_label.grid(row=2, column=0)

        #show fcf of stock
        self.fcff = fcff_df.loc[stock, "FCFF"]
        self.shares_out = fcff_df.loc[stock, "Shares outstanding"]
        self.fcf = self.fcff/self.shares_out
        self.fcf_label = Label(self.main_frame, text=f"FCF: \n{self.fcf}", font="Helvetica 10")
        self.fcf_label.grid(row=2, column=1)

        #show fair value stat
        self.fair_value = fcff_df.loc[stock, "Fair value"]   
        self.fair_value_label = Label(self.main_frame, text= f"Fair value: \n{self.fair_value}", font='Helvetica 10')
        self.fair_value_label.grid(row=3, column=0)

        #show percentage undervalued stat
        self.percentage_undervalued = fcff_df.loc[stock, "Percentage undervalued"]   
        self.percentage_undervalued_label = Label(self.main_frame, text= f"Percentage undervalued: \n{self.percentage_undervalued}", font='Helvetica 10')
        self.percentage_undervalued_label.grid(row=3, column=1)


    #function to populate button frame
    def update_buttons_frame(self):
        self.button_frame = Frame(self.master)

        self.back_button = Button(self.button_frame, text="Back", command=lambda: self.next(self.idx - 1))
        self.back_button.grid(row=0, column=0, pady="10", padx="10")

        self.next_button = Button(self.button_frame, text="Next", command=lambda: self.next(self.idx + 1))
        self.next_button.grid(row=0, column=1)

        self.like_button = Button(self.button_frame, text="Like", command=self.like)
        self.like_button.grid(row=1, column=0, pady="5", padx="10")

        #toggle like button based on whether stock is in watchlist
        with open("SGXstocks/Cache/watchlist.txt", "r") as watchlist:
            lines = watchlist.readlines()
        if str(self.current_stock + '\n') in lines:
            self.like_button.config(relief="sunken")

        self.watchlist_button = Button(self.button_frame, text="Watchlist", command=self.watchlist)
        self.watchlist_button.grid(row=1, column=1, pady="5", padx="10")

        self.button_frame.grid(row=1, column=0)

    ##### function to make buttons interactable #####

    #function for next and back buttons
    def next(self, idx):
        #update main frame
        self.idx = idx
        self.current_stock = fcff_df.index[self.idx]
        self.update_main_frame(self.current_stock)

        #toggle like button based on whether stock is in watchlist
        with open("SGXstocks/Cache/watchlist.txt", "r") as watchlist:
            lines = watchlist.readlines()
        if str(self.current_stock + '\n') in lines:
            self.like_button.config(relief="sunken")
        else:
            self.like_button.config(relief="raised")

    #function for like button
    def like(self):     
        if self.like_button.config('relief')[-1] == 'sunken':
            self.like_button.config(relief="raised")
            with open("SGXstocks/Cache/watchlist.txt", "r") as f:
                lines = f.readlines()
            with open("SGXstocks/Cache/watchlist.txt", "w") as f:
                for line in lines:
                    if line.strip("\n") != self.current_stock:
                        f.write(line)
        else:
            with open("SGXstocks/Cache/watchlist.txt", "a") as myfile:
                myfile.write(f"{self.current_stock}\n")
            self.like_button.config(relief="sunken")

    def watchlist(self):
        #function for view button
        def view_watchlist_stock(stock):
            watchlist_window.destroy()
            self.update_main_frame(stock)
            self.current_stock = stock
            self.update_buttons_frame()

            #update self.idx to that of stock
            self.idx = list(fcff_df.index).index(stock)

        #function for delete button
        def delete_watchlist_stock(stock):
            with open("SGXstocks/Cache/watchlist.txt", "r") as f:
                lines = f.readlines()
            with open("SGXstocks/Cache/watchlist.txt", "w") as f:
                for line in lines:
                    if line.strip("\n") != stock:
                        f.write(line)
            
            idx = Lines.index(stock+'\n')
            labels[idx].destroy()
            view_buttons[idx].destroy()
            delete_buttons[idx].destroy()

            if len(lines) == 1:
                Label(second_frame, text='Watchlist is currently empty', font='Helvetica 10').grid(column=0)

            #untoggle like button on main window if stock on that window is removed from watchlist
            if stock == self.current_stock:
                self.update_buttons_frame()
        
        #function for search button
        def search():
            search_ticker = search_entry.get()
            if search_ticker in fcff_df.index:
                view_watchlist_stock(search_ticker)
        
            else:
                messagebox.showerror("Error","Sorry the ticker you entered was not found within this spreadsheet")
                return

        #create new window over current window
        watchlist_window = Toplevel(self.master)
        watchlist_window.title("Watchlist")
        watchlist_window.geometry("400x500")

        #create search bar
        search_frame = Frame(watchlist_window)
        search_frame.pack()
        search_entry = Entry(search_frame)
        search_entry.pack(side=LEFT)
        search_button = Button(search_frame, text='Search', command=search)
        search_button.pack(side=LEFT)

        ##### scroll button #####
        # Create A Main Frame
        main_frame = Frame(watchlist_window)
        main_frame.pack(fill=BOTH, expand=1)

        # Create A Canvas
        my_canvas = Canvas(main_frame)
        my_canvas.pack(side=LEFT, fill=BOTH, expand=1)

        # Add A Scrollbar To The Canvas
        my_scrollbar = ttk.Scrollbar(main_frame, orient=VERTICAL, command=my_canvas.yview)
        my_scrollbar.pack(side=RIGHT, fill=Y)

        # Configure The Canvas
        my_canvas.configure(yscrollcommand=my_scrollbar.set)
        my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))

        def _on_mouse_wheel(event):
            my_canvas.yview_scroll(-1 * int((event.delta / 120)), "units")

        my_canvas.bind_all("<MouseWheel>", _on_mouse_wheel)

        # Create ANOTHER Frame INSIDE the Canvas
        second_frame = Frame(my_canvas)

        # Add that New frame To a Window In The Canvas
        my_canvas.create_window((0,0), window=second_frame, anchor="nw")

        ##### end of scroll bar #####

        #get list of stocks in watchlist
        file1 = open('SGXstocks/Cache/watchlist.txt', 'r')
        Lines = file1.readlines()

        if len(Lines) == 0:
            Label(second_frame, text='Watchlist is currently empty', font='Helvetica 10').grid(column=0)

        labels = []     #create empty lists to reference which ones to delete later on
        view_buttons = []
        delete_buttons = []
        for i in range(len(Lines)):
            watchlist_stock_label = Label(second_frame, text=Lines[i], font='Helvetica 10')
            watchlist_stock_label.grid(row=i, column=0)
            watchlist_stock_button = Button(second_frame, text='View', command=lambda i=i: view_watchlist_stock(Lines[i].strip()))
            watchlist_stock_button.grid(row=i, column=1)
            delete_watchlist_stock_button = Button(second_frame, text='Remove', command=lambda i=i:delete_watchlist_stock(Lines[i].strip()))
            delete_watchlist_stock_button.grid(row=i, column=2)

            labels.append(watchlist_stock_label)
            view_buttons.append(watchlist_stock_button)
            delete_buttons.append(delete_watchlist_stock_button)



root = Tk()
StonksApp(root)
root.mainloop()
