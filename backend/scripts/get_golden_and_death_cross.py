import warnings
from database.session import get_session
from database.models import Stock
from backend.scripts.functions.golden_cross import analyze_stock_for_golden_cross
from backend.scripts.functions.death_cross import analyze_stock_for_death_cross
from backend.scripts.functions.get_historical_data_by_date_range import (
    get_historical_data_by_date_range,
)
from datetime import datetime

# Ignore FutureWarning
warnings.simplefilter(action="ignore", category=FutureWarning)


def main():
    session = get_session()
    print("Starting analysis...")
    stocks = (
        session.query(Stock).filter(Stock.market == "MAIN")
        # .filter(Stock.ticker == "XTB.WA")[:500]
    )
    start_date = "2023-03-01"
    end_date = datetime.today().strftime("%Y-%m-%d")
    golden_cross_stocks = []
    death_cross_stocks = []

    for stock in stocks:
        data = get_historical_data_by_date_range(stock.ticker, start_date, end_date)

        if data.empty:
            print(f"No data available for {stock.ticker}")

        if not data.empty:
            golden_result = analyze_stock_for_golden_cross(stock, data)
            if golden_result:
                golden_cross_stocks.append(golden_result)

            death_result = analyze_stock_for_death_cross(stock, data)
            if death_result:
                death_cross_stocks.append(death_result)

    # Print the final list of stocks with Golden Cross occurrence
    for stock in golden_cross_stocks:
        print(
            f"{stock['ticker']} ({stock['name']}): Last Golden Cross on {stock['last_golden_cross_date']}"
        )

    for stock in death_cross_stocks:
        print(
            f"{stock['ticker']} ({stock['name']}): Last Death Cross on {stock['last_death_cross_date']}"
        )


if __name__ == "__main__":
    main()
