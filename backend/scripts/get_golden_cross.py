import warnings
from database.session import get_session
from database.models import Stock
from backend.scripts.functions.golden_cross import analyze_stock_for_golden_cross
from datetime import datetime

# Ignore FutureWarning
warnings.simplefilter(action="ignore", category=FutureWarning)


def main():
    session = get_session()
    print("Starting analysis...")
    stocks = session.query(Stock).filter(Stock.market == "MAIN")[
        :500
    ]  # Example: Analyze the first 5 stocks

    start_date = "2023-03-01"
    end_date = datetime.today().strftime("%Y-%m-%d")

    for stock in stocks:
        analyze_stock_for_golden_cross(stock.ticker, start_date, end_date)


if __name__ == "__main__":
    main()
