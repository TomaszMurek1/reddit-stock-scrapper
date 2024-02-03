from database.session import get_session
from database.models import Stock
import warnings
from backend.scripts.functions.golden_cross import analyze_stock_for_golden_cross

# Ignore FutureWarning
warnings.simplefilter(action="ignore", category=FutureWarning)


def main():
    session = get_session()
    print("Starting analysis...")
    stocks = session.query(Stock).all()[:50]  # Example: Analyze the first 5 stocks

    start_date = "2023-03-01"
    end_date = "2024-01-15"

    for stock in stocks:
        analyze_stock_for_golden_cross(stock.ticker, start_date, end_date)


if __name__ == "__main__":
    main()
