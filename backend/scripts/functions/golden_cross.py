from datetime import datetime


def check_golden_cross(data):
    short_ma_period = 50
    long_ma_period = 200
    short_ma = data["Close"].rolling(window=short_ma_period, min_periods=1).mean()
    long_ma = data["Close"].rolling(window=long_ma_period, min_periods=1).mean()

    cross_over = (short_ma > long_ma) & (short_ma.shift(1) < long_ma.shift(1))
    if any(cross_over):
        return (
            cross_over[cross_over].index[-1].strftime("%Y-%m-%d")
        )  # Return the last date of Golden Cross
    return None


def analyze_stock_for_golden_cross(stock, data, volume_threshold=50000, days_limit=20):

    # Calculate the average volume for the last 'days_limit' days and compare with the threshold
    average_volume = (data["Close"] * data["Volume"]).tail(days_limit).mean()
    if average_volume < volume_threshold:
        print(f"Volume too low for {stock.name}")
        return None
    average_volume2 = (data["Close"] * data["Volume"]).tail(20).mean()
    print(average_volume2 / 1000)
    last_golden_cross_date = check_golden_cross(data)
    if last_golden_cross_date:
        # Check if the Golden Cross occurred within the last 'days_limit' days
        last_date = datetime.strptime(last_golden_cross_date, "%Y-%m-%d")
        if (datetime.today() - last_date).days <= days_limit:
            return {
                "ticker": stock.ticker,
                "name": f"{stock.name}",
                "last_golden_cross_date": last_golden_cross_date,
            }
    return None
