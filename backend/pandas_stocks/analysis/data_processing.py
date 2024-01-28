import yfinance as yf
import pandas as pd


def get_historical_data_by_range_date(stock, start_date, end_date):
    try:
        data = yf.download(stock, start=start_date, end=end_date)
        return data
    except KeyError:
        print(
            f"Error retrieving data for {stock}. This stock might be delisted or the ticker symbol could be incorrect."
        )
        return pd.DataFrame()


def calculate_moving_averages(data):
    data["MA50"] = data["Close"].rolling(window=50).mean()
    data["MA200"] = data["Close"].rolling(window=200).mean()
    return data


def get_stock_data(ticker, period="1mo", interval="1d"):
    stock_data = yf.download(ticker, period=period, interval=interval)
    return stock_data
