import pandas_datareader as pdr
import pandas as pd
from datetime import date
name = 'MGNT'
today = date.today()
f = pdr.get_data_moex(['USD000UTSTOM', name], '2022-07-02', today)
print(f['CLOSE'])