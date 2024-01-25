import pandas as pd
from typing import Union, Literal


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


def check_death_cross(data):
    days_to_check = min(15, len(data))

    cross_indices = data.index[
        (data["MA50"] < data["MA200"])
        & (data["MA50"].shift(1) > data["MA200"].shift(1))
    ]

    recent_crosses = cross_indices[cross_indices > data.index[-days_to_check]]

    if not recent_crosses.empty:
        # Return the most recent date of occurrence
        return True, recent_crosses[-1]
    else:
        return False, None
