import pandas as pd
from backend.scripts.functions.get_historical_data_by_date_range import (
    get_historical_data_by_date_range,
)


def check_golden_cross(
    data: pd.DataFrame, short_ma_period: int = 50, long_ma_period: int = 200
) -> bool:
    """
    Check for a Golden Cross in the provided data.

    :param data: DataFrame containing stock price data.
    :param short_ma_period: Period for the short moving average.
    :param long_ma_period: Period for the long moving average.
    :return: True if a Golden Cross is found, False otherwise.
    """
    short_ma = data["Close"].rolling(window=short_ma_period, min_periods=1).mean()
    long_ma = data["Close"].rolling(window=long_ma_period, min_periods=1).mean()

    # Find the Golden Cross
    cross_over = (short_ma > long_ma) & (short_ma.shift(1) < long_ma.shift(1))
    return any(cross_over)


def analyze_stock_for_golden_cross(stock_symbol: str, start_date: str, end_date: str):
    """
    Analyze a single stock for a Golden Cross event within a given date range.

    :param stock_symbol: The stock symbol to analyze.
    :param start_date: Start date for the analysis period.
    :param end_date: End date for the analysis period.
    :return: Result of the Golden Cross analysis.
    """
    data = get_historical_data_by_date_range(stock_symbol, start_date, end_date)
    if data.empty:
        print(f"No data available for {stock_symbol}")
        return False
    if check_golden_cross(data):
        print(
            f"Golden Cross found for {stock_symbol} between {start_date} and {end_date}"
        )
        return True
    else:
        print(f"No Golden Cross found for {stock_symbol}")
        return False
