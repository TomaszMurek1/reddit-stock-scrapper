from .data_processing import get_historical_data_by_range_date


def is_consolidating(df, percentage=5):
    recent_candlestick = df[-15:]
    # print(recent_candlestick)
    avg_volume = recent_candlestick["Volume"].mean()
    max_close = recent_candlestick["Close"].max()
    min_close = recent_candlestick["Close"].min()
    volume = avg_volume * min_close

    threshold = 1 - (percentage / 100)
    if min_close > (max_close * threshold) and volume > 100000:
        return True
    return False


def analyze_stock(stock, start_date, end_date, check_function):
    # print(f"Analyzing {stock.ticker}...")
    data = get_historical_data_by_range_date(stock.ticker + ".WA", start_date, end_date)
    if data.empty:
        return None
    if check_function(data):
        return stock
    return None


def consolidation_case(stocks, start_date, end_date):
    consolidating_stocks = []
    for stock in stocks[0:500]:
        result = analyze_stock(stock, start_date, end_date, is_consolidating)
        if result:
            consolidating_stocks.append(result)
    return consolidating_stocks
