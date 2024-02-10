import requests
import pandas as pd
from bs4 import BeautifulSoup
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
from database.models import (
    GpwBalanceSheet,
    GpwCashFlowStatement,
    GpwProfitAndLossStatement,
)
from backend.scripts.helpers.dictionaries import (
    Gpw_Balance_Sheet_MAP,
    Gpw_Profit_And_Loss_Statement_MAP,
    Gpw_Cash_Flow_Statement_MAP,
)

ticker, biznesRadarId = "DELKO.WA", "DELKO"
base_url = "https://www.biznesradar.pl/raporty-finansowe-"
URL_TO_MAP_AND_CLASS = {
    f"{base_url}przeplywy-pieniezne/{biznesRadarId}": (
        Gpw_Cash_Flow_Statement_MAP,
        GpwCashFlowStatement,
    ),
    f"{base_url}rachunek-zyskow-i-strat/{biznesRadarId}": (
        Gpw_Profit_And_Loss_Statement_MAP,
        GpwProfitAndLossStatement,
    ),
    f"{base_url}bilans/{biznesRadarId}": (
        Gpw_Balance_Sheet_MAP,
        GpwBalanceSheet,
    ),
}


def fetch_soup(url):
    response = requests.get(url)
    return BeautifulSoup(response.text, "html.parser")


def extract_table_data(soup):
    table = soup.find("table", attrs={"class": "report-table"})
    rows = table.find_all("tr")[1:]  # Skip header row
    data = []

    for row in rows:
        cells = row.find_all("td")[:-1]  # Skip last column
        row_data = [extract_cell_data(cell, index) for index, cell in enumerate(cells)]
        data.append(row_data)
    return data


def extract_cell_data(cell, index):
    if index == 0:
        return find_deepest_text(cell)
    else:
        span_with_class = cell.find("span", class_="value")
        if span_with_class:
            text = span_with_class.text.replace(" ", "").strip()
            return parse_to_float(text)
        else:
            # Return None or a suitable default value if the span is not found
            return None


def find_deepest_text(element):
    if not element.find_all():
        return element.text.strip()
    for child in element.children:
        return find_deepest_text(child)


def parse_to_float(text):
    try:
        return float(text) if text else None
    except ValueError:
        return text


def transform_data_to_dataframe(data, _map):
    df = pd.DataFrame(data).T
    df.columns = [_map.get(col, col) for col in df.iloc[0]]
    return df.drop(df.index[0])


def initialize_database():
    Base = declarative_base()
    engine = create_engine("sqlite:///database/stocks.db", echo=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def save_data_to_database(session, df, tableClass, ticker):
    for _, row in df.iterrows():
        row_data = dict(zip(df.columns, row))
        row_data["company_name"] = ticker
        clean_row_data(row_data)
        record = tableClass(**row_data)
        session.add(record)
    session.commit()


def clean_row_data(row_data):
    for column, value in row_data.items():
        if value is not None and column != "publication_date":
            try:
                row_data[column] = float(value)
            except ValueError:
                continue


if __name__ == "__main__":
    url_map = {
        "bilans": f"{base_url}bilans/{biznesRadarId}",
        "rachunek-zyskow-i-strat": f"{base_url}rachunek-zyskow-i-strat/{biznesRadarId}",
        "przeplywy-pieniezne": f"{base_url}przeplywy-pieniezne/{biznesRadarId}",
    }
    session = initialize_database()
    for url_key, full_url in url_map.items():
        map_, class_ = URL_TO_MAP_AND_CLASS[full_url]
        soup = fetch_soup(full_url)
        data = extract_table_data(soup)
        df = transform_data_to_dataframe(data, map_)
        save_data_to_database(session, df, class_, ticker)
    session.close()
