import pandas as pd

df1 = pd.read_csv("FSM/PriceHistory/fsm-pricehistory-updated.csv", index_col=[0])
df2 = pd.read_csv("FSM/PriceHistory/fsm-pricehistory-2021-07-28.csv", index_col=[0])

df3 = df1.combine_first(df2)
df3.to_csv("FSM/PriceHistory/fsm-pricehistory-updated.csv", index=True)