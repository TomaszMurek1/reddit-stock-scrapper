from datetime import datetime


def get_death_cross(data):
    short_ma_period = 50
    long_ma_period = 200
    short_ma = data["Close"].rolling(window=short_ma_period, min_periods=1).mean()
    long_ma = data["Close"].rolling(window=long_ma_period, min_periods=1).mean()

    cross_under = (short_ma < long_ma) & (short_ma.shift(1) > long_ma.shift(1))
    if any(cross_under):
        return cross_under[cross_under].index[-1].strftime("%Y-%m-%d")
    return None


def analyze_stock_for_death_cross(stock, data, volume_threshold=50000, days_limit=20):

    # Check if the volume and Death Cross conditions are met
    average_volume = (data["Close"] * data["Volume"]).tail(days_limit).mean()
    if average_volume < volume_threshold:
        print(f"Volume too low for {stock.name}")
        return None

    last_death_cross_date = get_death_cross(data)
    if last_death_cross_date:
        last_date = datetime.strptime(last_death_cross_date, "%Y-%m-%d")
        if (datetime.today() - last_date).days <= days_limit:
            return {
                "ticker": stock.ticker,
                "name": f"{stock.name}",
                "last_death_cross_date": last_death_cross_date,
            }
    return None
