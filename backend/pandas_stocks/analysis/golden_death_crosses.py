import pandas as pd
from typing import Union, Literal
from .data_processing import get_stock_data
from .data_processing import get_historical_data_by_range_date
from .data_processing import calculate_moving_averages


def check_golden_cross(
    data: pd.DataFrame, days_after_cross: int = 30
) -> Union[
    tuple[Literal[True], pd.Timestamp, float], tuple[Literal[False], None, None]
]:
    """
    Check for a Golden Cross in the last 55 days and
    return the date of occurrence and the highest price
    in the 30 days following the Golden Cross.
    """
    print("Check golden cross")

    days_to_check = min(55, len(data))
    if days_to_check < 55:
        print(
            "Warning: Insufficient data (less than 55 days). \
            Checking available data only."
        )

    cross_indices = data.index[
        (data["MA50"] > data["MA200"])
        & (data["MA50"].shift(1) < data["MA200"].shift(1))
    ]

    recent_crosses = cross_indices[cross_indices > data.index[-days_to_check]]

    if not recent_crosses.empty:
        most_recent_cross = recent_crosses[-1]
        # Calculate the end date for the highest price search
        end_date = min(
            data.index[-1], most_recent_cross + pd.DateOffset(days=days_after_cross)
        )
        highest_price = data["Close"][most_recent_cross:end_date].max()

        return True, most_recent_cross, highest_price
    else:
        return False, None, None


def check_death_cross(
    data: pd.DataFrame, days_after_cross: int = 30
) -> Union[
    tuple[Literal[True], pd.Timestamp, float], tuple[Literal[False], None, None]
]:
    """
    Check for a Death Cross in the last 55 days and
    return the date of occurrence and the lowest price
    in the 30 days following the Death Cross.
    """
    print("Check death cross")

    days_to_check = min(55, len(data))
    if days_to_check < 55:
        print(
            "Warning: Insufficient data (less than 55 days). \
            Checking available data only."
        )

    cross_indices = data.index[
        (data["MA50"] < data["MA200"])
        & (data["MA50"].shift(1) > data["MA200"].shift(1))
    ]

    recent_crosses = cross_indices[cross_indices > data.index[-days_to_check]]

    if not recent_crosses.empty:
        most_recent_cross = recent_crosses[-1]
        # Calculate the end date for the lowest price search
        end_date = min(
            data.index[-1], most_recent_cross + pd.DateOffset(days=days_after_cross)
        )
        lowest_price = data["Close"][most_recent_cross:end_date].min()

        return True, most_recent_cross, lowest_price
    else:
        return False, None, None


def analyze_stock_cross(stock, start_date, end_date, check_cross_function):
    print(f"Analyzing {stock.ticker}...")
    data = get_historical_data_by_range_date(stock.ticker + ".WA", start_date, end_date)
    if data.empty:
        return None
    ma_data = calculate_moving_averages(data)
    cross_result = check_cross_function(ma_data)
    if cross_result[0]:
        return stock.ticker, cross_result[1], cross_result[2]
    return None


def golden_cross_case(stocks, start_date, end_date):
    golden_cross_stocks = []
    for stock in stocks[:50]:
        result = analyze_stock_cross(stock, start_date, end_date, check_golden_cross)
        if result:
            golden_cross_stocks.append(result)
    return golden_cross_stocks


def death_cross_case(stocks, start_date, end_date):
    death_cross_stocks = []
    for stock in stocks[250:350]:
        result = analyze_stock_cross(stock, start_date, end_date, check_death_cross)
        if result:
            death_cross_stocks.append(result)
    return death_cross_stocks
