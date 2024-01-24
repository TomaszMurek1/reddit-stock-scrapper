import yfinance as yf
import pandas as pd
import warnings
from sqlalchemy.orm import sessionmaker
from database.models import engine
from database.models import Stock
Session = sessionmaker(bind=engine)
session = Session()

# Ignore FutureWarning
warnings.simplefilter(action='ignore', category=FutureWarning)

def get_historical_data(stock, start_date, end_date):
    try:
        data = yf.download(stock, start=start_date, end=end_date)
        return data
    except KeyError:
        print(f"Error retrieving data for {stock}. This stock might be delisted or the ticker symbol could be incorrect.")
        return pd.DataFrame()

def calculate_moving_averages(data):
    data['MA50'] = data['Close'].rolling(window=50).mean()
    data['MA200'] = data['Close'].rolling(window=200).mean()
    return data

def check_golden_cross(data, days_after_cross=30):
    """
    Check for a Golden Cross in the last 55 days and return the date of occurrence and the highest price in the 30 days following the Golden Cross.
    """
    print("Check golden cross")

    days_to_check = min(55, len(data))
    if days_to_check < 55:
        print("Warning: Insufficient data (less than 55 days). Checking available data only.")

    cross_indices = data.index[(data['MA50'] > data['MA200']) & (data['MA50'].shift(1) < data['MA200'].shift(1))]

    recent_crosses = cross_indices[cross_indices > data.index[-days_to_check]]
    
    if not recent_crosses.empty:
        most_recent_cross = recent_crosses[-1]
        # Calculate the end date for the highest price search
        end_date = min(data.index[-1], most_recent_cross + pd.DateOffset(days=days_after_cross))
        highest_price = data['Close'][most_recent_cross:end_date].max()

        return True, most_recent_cross, highest_price
    else:
        return False, None, None



def check_death_cross(data):
    days_to_check = min(15, len(data))
    
    cross_indices = data.index[(data['MA50'] < data['MA200']) & (data['MA50'].shift(1) > data['MA200'].shift(1))]

    recent_crosses = cross_indices[cross_indices > data.index[-days_to_check]]
    
    if not recent_crosses.empty:
        # Return the most recent date of occurrence
        return True, recent_crosses[-1]
    else:
        return False, None


def main():
    print('hello')
    stocks = session.query(Stock).all()
    print(stocks)
    for stock in stocks:
         print(f"Ticker: {stock.ticker}, Name: {stock.name}")

    #stocks = ["PKN.WA", "TAR.WA","WSE:ALL"]  # Example stock symbols
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
        golden_cross, date_of_golden_cross, highest_price = check_golden_cross(ma_data)
        #death_cross, date_of_death_cross = check_death_cross(ma_data)
        if golden_cross:
            # Get the closing price on the date of the death cross
            golden_cross_price = data.loc[date_of_golden_cross, 'Close']
            
            # Get the most recent closing price
            last_price = data.iloc[-1]['Close']

            # Calculate the percentage change
            percentage_change = ((last_price - golden_cross_price) / golden_cross_price) * 100
            highest_change = ((highest_price - golden_cross_price) / golden_cross_price) * 100
            golden_cross_stocks.append(f"{stock.Ticker} - {stock.Name} - Death Cross on {date_of_golden_cross.date()} - Death Cross Price: {golden_cross_price:.2f}, Last Price: {last_price:.2f}, Change: {percentage_change:.2f}%, Highest Price: {highest_price:.2f}, Change: {highest_change:.2f}")
           
    print(golden_cross_stocks)
    for stock_info in golden_cross_stocks:
        print(stock_info)

if __name__ == "__main__":
    main()