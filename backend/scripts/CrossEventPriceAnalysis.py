import pandas as pd
import yfinance as yf


def calculate_sma(data, window):
    return data["Close"].rolling(window=window).mean()


def identify_crossovers(data, column1, column2):
    crosses = []
    for index in range(1, len(data)):
        prev_row = data.iloc[index - 1]
        curr_row = data.iloc[index]
        if (prev_row[column1] < prev_row[column2]) and (
            curr_row[column1] > curr_row[column2]
        ):
            crosses.append((data.index[index], "Golden Cross", f"{column1}/{column2}"))
        elif (prev_row[column1] > prev_row[column2]) and (
            curr_row[column1] < curr_row[column2]
        ):
            crosses.append((data.index[index], "Death Cross", f"{column1}/{column2}"))
    return crosses


def analyze_after_cross(data, crosses, days_to_analyze=30):
    analysis_results = []
    for date, cross_type, sma_cross in crosses:
        start_index = data.index.get_loc(date)
        end_index = min(start_index + days_to_analyze, len(data) - 1)
        after_cross_data = data.iloc[start_index : end_index + 1]
        start_price = data.at[date, "Close"]
        max_price = after_cross_data["Close"].max()
        max_price_date = after_cross_data["Close"].idxmax()
        max_price_change = (max_price - start_price) / start_price
        price_change = (after_cross_data["Close"].iloc[-1] - start_price) / start_price
        analysis_results.append(
            (
                cross_type,
                sma_cross,
                date,
                start_price,
                max_price,
                max_price_date,
                max_price_change,
                price_change,
            )
        )
    return analysis_results


def analyze_stock(ticker, start_date, end_date, analysis_days):
    data = yf.download(ticker, start=start_date, end=end_date)
    if data.empty:
        print(f"No data found for {ticker}")
        return

    data["SMA20"] = calculate_sma(data, 20)
    data["SMA50"] = calculate_sma(data, 50)
    data["SMA200"] = calculate_sma(data, 200)

    crosses = identify_crossovers(data, "SMA50", "SMA200") + identify_crossovers(
        data, "SMA20", "SMA50"
    )
    analysis_results = analyze_after_cross(data, crosses, days_to_analyze=analysis_days)

    sorted_results = sorted(analysis_results, key=lambda x: (x[0], x[1], x[2]))
    for result in sorted_results:
        print(
            f"{ticker} - Type: {result[0]}, SMA Cross: {result[1]}, Date of Cross: {result[2].date()}, Price at Cross: {result[3]:.2f}, Max Price: {result[4]:.2f} on {result[5].date()}, Max Price Change: {result[6]:.2%}, Price Change after {analysis_days} days: {result[7]:.2%}"
        )


def main():
    tickers = ["ASB.WA", "AAPL", "MSFT"]  # Add your desired tickers here
    start_date = "2020-01-01"
    end_date = "2024-01-01"
    analysis_days = 30

    all_results = []  # List to store all results

    for ticker in tickers:
        data = yf.download(ticker, start=start_date, end=end_date)
        if data.empty:
            print(f"No data found for {ticker}")
            continue

        data["SMA20"] = calculate_sma(data, 20)
        data["SMA50"] = calculate_sma(data, 50)
        data["SMA200"] = calculate_sma(data, 200)

        crosses = identify_crossovers(data, "SMA50", "SMA200") + identify_crossovers(
            data, "SMA20", "SMA50"
        )
        analysis_results = analyze_after_cross(
            data, crosses, days_to_analyze=analysis_days
        )

        for result in analysis_results:
            all_results.append(
                [
                    ticker,
                    result[0],
                    result[1],
                    result[2],
                    result[3],
                    result[4],
                    result[5],
                    result[6],
                    result[7],
                ]
            )

    # Creating DataFrame from the results
    results_df = pd.DataFrame(
        all_results,
        columns=[
            "Ticker",
            "Type",
            "SMA Cross",
            "Date of Cross",
            "Price at Cross",
            "Max Price",
            "Max Price Date",
            "Max Price Change",
            "Price Change after 30 days",
        ],
    )

    # Saving results to CSV
    results_df.to_csv("stock_cross_analysis_results.csv", index=False)
    print("Saved results to 'stock_cross_analysis_results.csv'")


if __name__ == "__main__":
    main()
