import pandas as pd
import yfinance


def get_historical_data_by_date_range(stock, start_date, end_date):
    try:
        data = yfinance.download(stock, start=start_date, end=end_date)
        return data
    except KeyError:
        print(
            f"Error retrieving data for {stock}. This stock might be delisted or the ticker symbol could be incorrect."
        )
        return pd.DataFrame()
