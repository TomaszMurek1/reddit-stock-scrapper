import warnings
from .analysis.golden_death_crosses import check_golden_cross
from .analysis.data_processing import get_historical_data
from .analysis.data_processing import calculate_moving_averages
from database.models import Stock
from database.session import get_session

session = get_session()

# Ignore FutureWarning
warnings.simplefilter(action="ignore", category=FutureWarning)


def main():
    print("hello")
    stocks = session.query(Stock).all()
    print(stocks)
    for stock in stocks:
        print(f"Ticker: {stock.ticker}, Name: {stock.name}")

    # stocks = ["PKN.WA", "TAR.WA","WSE:ALL"]  # Example stock symbols
    start_date = "2023-01-01"
    end_date = "2024-01-21"
    golden_cross_stocks = []
    death_cross_stocks = []

    for stock in stocks[0:500]:
        print(f"Analyzing {stock.ticker}...")
        data = get_historical_data(stock.ticker + ".WA", start_date, end_date)
        if data.empty:
            continue
        ma_data = calculate_moving_averages(data)
        (golden_cross, date_of_golden_cross, highest_price) = check_golden_cross(
            ma_data
        )

        # death_cross, date_of_death_cross = check_death_cross(ma_data)
        if golden_cross:
            # Get the closing price on the date of the death cross
            golden_cross_price = data.loc[date_of_golden_cross, "Close"]

            # Get the most recent closing price
            last_price = data.iloc[-1]["Close"]

            # Calculate the percentage change
            percentage_change = (
                (last_price - golden_cross_price) / golden_cross_price
            ) * 100
            highest_change = (
                (highest_price - golden_cross_price) / golden_cross_price
            ) * 100
            golden_cross_stocks.append(
                f"{stock.ticker} - {stock.name} - \
                  Death Cross on {date_of_golden_cross.date()} \
                    - Death Cross Price: {golden_cross_price:.2f}, \
                        Last Price: {last_price:.2f}, \
                            Change: {percentage_change:.2f}%, \
                            Highest Price: {highest_price:.2f}, \
                                Change: {highest_change:.2f}"
            )

    print(golden_cross_stocks)
    for stock_info in golden_cross_stocks:
        print(stock_info)


if __name__ == "__main__":
    main()
