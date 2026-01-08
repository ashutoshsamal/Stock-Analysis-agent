import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

symbol = 'ABB.NS'
start_date = '2024-01-01'
end_date = '2025-05-31'

stock = yf.Ticker(symbol)
print(stock.info)

print(stock.quarterly_income_stmt)


# data = stock.history(start=start_date, end=end_date)
#
# data['20_Day_MA'] = data['Close'].rolling(window=20).mean()
#
# data['Daily_Return'] = data['Close'].pct_change() * 100
#
# print(data.columns)
# print(data["Volume"])
