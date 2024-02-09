import warnings
from database.session import get_session
from database.models import Stock
from backend.scripts.functions.get_historical_data_by_date_range import (
    get_historical_data_by_date_range,
)

warnings.simplefilter(action="ignore", category=FutureWarning)


def is_consolidating(df, percentage=5):
    recent_candlestick = df[-15:]
    avg_volume = recent_candlestick["Volume"].mean()
    max_close = recent_candlestick["Close"].max()
    min_close = recent_candlestick["Close"].min()
    volume = avg_volume * min_close

    threshold = 1 - (percentage / 100)
    return min_close > (max_close * threshold) and volume > 100000


def analyze_stock(stock, start_date, end_date, check_function):
    data = get_historical_data_by_date_range(f"{stock.ticker}", start_date, end_date)
    return stock if not data.empty and check_function(data) else None


def consolidation_case(stocks, start_date, end_date):
    consolidating_stocks = []
    for stock in stocks[:800]:
        result = analyze_stock(stock, start_date, end_date, is_consolidating)
        if result:
            consolidating_stocks.append(result)
    return consolidating_stocks


def main():
    # Define your main logic here
    session = get_session()
    print("Starting analysis...")
    stocks = (
        session.query(Stock).filter(Stock.market == "MAIN").limit(800).all()
    )  # Example: Analyze the first 5 stocks
    start_date = "2023-03-01"
    end_date = "2024-02-09"

    consolidating_stocks = consolidation_case(stocks, start_date, end_date)

    # Print or further process the results as needed
    for stock in consolidating_stocks:
        print(f"Consolidating Stock: {stock.ticker}")


if __name__ == "__main__":
    main()
