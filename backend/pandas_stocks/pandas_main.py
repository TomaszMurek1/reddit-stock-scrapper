import warnings
from .analysis.golden_death_crosses import golden_cross_case
from .analysis.golden_death_crosses import death_cross_case
from .analysis.consolidation import consolidation_case
from database.models import Stock
from database.session import get_session

session = get_session()

# Ignore FutureWarning
warnings.simplefilter(action="ignore", category=FutureWarning)


def main():
    print("hello")
    stocks = session.query(Stock).all()
    for stock in stocks[:5]:
        print(f"Ticker: {stock.ticker}, Name: {stock.name}")
    case_to_execute = "is_consolidating"
    # stocks = ["PKN.WA", "TAR.WA","WSE:ALL"]  # Example stock symbols

    cases = {
        "golden_cross": golden_cross_case,
        "death_cross": death_cross_case,
        "is_consolidating": consolidation_case
        # Add other cases as needed
    }
    start_date = "2023-01-01"
    end_date = "2024-01-25"

    if case_to_execute in cases:
        result = cases[case_to_execute](stocks, start_date, end_date)
        if result:
            for r in result:
                print(f"{r.ticker} {r.name}")
            # print(
            #     f"{r[0]}: {case_to_execute} on {r[1].date()}, Highest price in last 30 days: {r[2]}"
            # )
        else:
            print(f"No results found for {case_to_execute} case.")
    else:
        print(f"No case found for {case_to_execute}")


if __name__ == "__main__":
    main()
