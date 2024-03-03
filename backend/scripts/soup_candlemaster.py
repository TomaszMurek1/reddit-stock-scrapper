from datetime import datetime, timedelta
import requests
import pandas as pd
from bs4 import BeautifulSoup
import yfinance as yf
import pdb
import warnings

# Ignore specific FutureWarnings from yfinance
warnings.filterwarnings(
    "ignore",
    message="The 'unit' keyword in TimedeltaIndex construction is deprecated")


def fetch_soup(url):
    response = requests.get(url, verify=False)
    return BeautifulSoup(response.text, "html.parser")


def extract_table_data(soup, date):
    # Extract headers from the <thead> section, skipping the first header
    table_head = soup.find('thead')
    headers = [header.text.strip() for header in table_head.find_all('th')][1:]

    # Add 'Date' header at the beginning
    headers.insert(0, 'Date')

    table_body = soup.find('tbody')
    rows = table_body.find_all('tr')

    data = []
    for row in rows:
        cells = row.find_all('td')  # Use 'td' for data cells
        row_data = [cell.text.strip() for cell in cells]
        # Prepend the date to the row data
        row_data.insert(0, date)
        data.append(row_data)

    return data, headers


links_with_dates = [
    {
        "period":
        "Luty",
        "date":
        "2024-01-31",
        "url":
        "https://candlemaster.pl/competitions/7aa8d158-7301-4bdf-9862-953530c031fc/show"
    },
    {
        "period":
        "Styczen",
        "date":
        "2023-01-02",
        "url":
        "https://candlemaster.pl/competitions/15fdb4ac-8e03-4058-87cb-a9ed30ea7eeb/show"
    },
    {
        "period":
        "Grudzien",
        "date":
        "2023-12-01",
        "url":
        "https://candlemaster.pl/competitions/0476ccb7-37c4-4cff-959a-7e808bc3142e/show"
    },
    {
        "period":
        "Listopad",
        "date":
        "2023-11-01",
        "url":
        "https://candlemaster.pl/competitions/f12d4f13-79cd-4a38-8e2c-709a69416325/show"
    },
]

# User-specified dates

date2 = '2023-11-30'
date3 = '2023-12-29'
date4 = '2024-01-31'
date5 = '2024-02-29'
dates = [date5, date4, date3, date2]


def calculate_percentage_change(old_price, new_price):
    if old_price and new_price:
        difference = (new_price - old_price) / old_price * 100
        return difference
    return None


def fetch_prices_for_dates(ticker, original_date, future_dates):
    try:
        # Find the earliest and latest date to minimize the data fetched
        earliest_date = "2023-10-30"  # min(original_date, future_dates[2])
        latest_date = max([original_date] + future_dates)

        earliest_date_obj = datetime.strptime(earliest_date, "%Y-%m-%d")
        latest_date_obj = datetime.strptime(latest_date, "%Y-%m-%d")

        stock = yf.Ticker(ticker)
        hist = stock.history(start=earliest_date_obj - timedelta(days=1),
                             end=latest_date_obj + timedelta(days=1))

        # Convert hist.index to a list of string-formatted dates for comparison
        formatted_hist_dates = hist.index.strftime('%Y-%m-%d').tolist()

        # Extract the closing prices for the original and future dates
        prices = {date: None for date in [original_date, *future_dates]}

        for date in prices.keys():

            if date in formatted_hist_dates:
                prices[date] = hist.loc[hist.index == date, 'Close'].values[0]
        return prices
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}


def transform_row_data(row):
    """
    Transforms a single row of the DataFrame into a list of dictionaries
    representing the transformed data for Typ L and Typ S occurrences.
    """
    transformed_data = []
    date = row['Date']
    user = row['Uczestnik(nazwa z Twittera)']
    # Define a mapping for the occurrences of Typ L and Typ S
    type_positions = [('L', 3), ('S', 5), ('L', 7), ('S', 9)]

    for typ, pos in type_positions:
        if row.iloc[
                pos] != '-----':  # Check if the value at the position is not the placeholder
            transformed_data.append({
                'Date': date,
                'User': user,
                'Type': typ,
                'Ticker': row.iloc[pos]
            })

    return transformed_data


def calculate_prediction_accuracy(df):
    """
    Calculate and rank users based on the accuracy of their stock price predictions, handling None or NaN values.
    
    Args:
    df (DataFrame): A pandas DataFrame with columns ['Date', 'User', 'Type', 'Ticker', 'Percentage Change']
    
    Returns:
    DataFrame: A DataFrame with columns ['User', 'Correct_Score_L', 'Correct_Score_S', 'Total_Correct_Score']
               ranked by 'Total_Correct_Score'.
    """

    # Convert '2024-02-01' column to numeric, coercing errors to NaN, then fill NaN with 0
    df['2024-02-29'] = pd.to_numeric(df['2024-02-29'],
                                     errors='coerce').fillna(0)

    # Calculate the score based on prediction accuracy
    df['Correct_Score'] = df.apply(lambda row: abs(row['2024-02-29']) if (
        (row['Type'] == 'L' and row['2024-02-29'] > 0) or
        (row['Type'] == 'S' and row['2024-02-29'] < 0)) else -abs(row[
            '2024-02-29']),
                                   axis=1)

    # Separate scores for L and S predictions
    df['Correct_Score_L'] = df.apply(lambda row: row['Correct_Score']
                                     if row['Type'] == 'L' else 0,
                                     axis=1)
    df['Correct_Score_S'] = df.apply(lambda row: row['Correct_Score']
                                     if row['Type'] == 'S' else 0,
                                     axis=1)

    def custom_aggregation(series):
        # Convert each value in the series by dividing by 100, adding 1, and then return the product of all values
        return (series / 100 + 1).prod()

    # Aggregate scores by user
    user_scores = df.groupby('User').agg({
        'Correct_Score_L': 'sum',
        'Correct_Score_S': 'sum'
    })
    user_scores['Total_Correct_Score'] = user_scores[
        'Correct_Score_L'] + user_scores['Correct_Score_S']

    # Sort by Total_Correct_Score for ranking
    user_ranking = user_scores.sort_values(by='Total_Correct_Score',
                                           ascending=False).reset_index()

    return user_ranking


if __name__ == "__main__":
    all_data = []
    headers = []

    # Fetch and compile table data
    for index, item in enumerate(links_with_dates):
        soup = fetch_soup(item["url"])
        table_data, extracted_headers = extract_table_data(soup, item["date"])

        if index == 0:
            headers = extracted_headers

        all_data.extend(table_data)

    df = pd.DataFrame(all_data, columns=headers)

    # Transform the DataFrame data
    transformed_data = [
        item for _, row in df.iterrows() for item in transform_row_data(row)
    ]
    new_df = pd.DataFrame(transformed_data)

    # Add columns for price changes and calculate them
    for i, date in enumerate(dates, start=1):
        new_df[f'{date}'] = None

    for index, row in new_df.head(2000).iterrows():
        ticker = f"{row['Ticker']}.WA"
        original_date_str = row['Date']
        original_date = datetime.strptime(original_date_str, "%Y-%m-%d")
        prices = fetch_prices_for_dates(ticker, original_date_str, dates)

        original_price = prices.get(original_date_str)

        for i, future_date_str in enumerate(dates, start=1):
            future_date = datetime.strptime(future_date_str, "%Y-%m-%d")
            if future_date > original_date:
                new_price = prices.get(future_date_str)
                percentage_change = calculate_percentage_change(
                    original_price, new_price)
                new_df.at[index, future_date_str] = percentage_change
            else:
                # Optionally handle the case where future_date is not after original_date
                print(
                    f"Skipping calculation for {future_date_str} as it is not")

    print(new_df)
    new_df.to_csv('candle_master.csv', index=False)

    ranked_users = calculate_prediction_accuracy(new_df)
    print(ranked_users)
    ranked_users.to_csv('ranked_users.csv', index=False)
