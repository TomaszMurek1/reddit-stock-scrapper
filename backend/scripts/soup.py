import requests
import pandas as pd
from bs4 import BeautifulSoup
from sqlalchemy.orm import sessionmaker
from database.models import CashFlowStatement
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

from backend.scripts.helpers.dictionaries import Cash_Flow_Statement_MAP

# Define a list of stock symbols you are interested in
# For demonstration, we'll use a small list, but for a real scenario, you might want a comprehensive list or a way to generate it
ticker = "DELKO.WA"
biznesRadarId = "DELKO"
urlRZiS = f"https://www.biznesradar.pl/raporty-finansowe-rachunek-zyskow-i-strat/{biznesRadarId}"
urlBilans = f"https://www.biznesradar.pl/raporty-finansowe-bilans/{biznesRadarId}"
urlPrzeplywy = (
    f"https://www.biznesradar.pl/raporty-finansowe-przeplywy-pieniezne/{biznesRadarId}"
)


response = requests.get(urlPrzeplywy)
soup = BeautifulSoup(response.text, "html.parser")
# Placeholder for stocks meeting the criteria
table = soup.find(
    "table", attrs={"class": "report-table"}
)  # Use the actual class or ID of the table
rows = table.find_all("tr")


def find_deepest_text(element):
    if not element.find_all():
        return element.text.strip()
    for child in element.children:
        return find_deepest_text(child)


all_row_data = []

for index, row in enumerate(rows):
    if index < 1:  # Skip the first 2 rows
        continue
    cells = row.find_all("td")[
        :-1
    ]  # Exclude the last column by slicing all but the last cell
    row_data = []
    for index, cell in enumerate(cells):
        if index == 0:  # For the first cell in each row, extract the deepest text
            cell_data = find_deepest_text(cell)
        else:  # For remaining cells, find a span with the specified class and get its text
            span_with_class = cell.find("span", class_="value")
            if span_with_class:
                text = span_with_class.text.replace(
                    " ", ""
                ).strip()  # Remove spaces and strip
            # Convert text to float if it's a numeric value, handle empty strings and None
            try:
                cell_data = float(text) if text else None
            except ValueError:
                cell_data = text
        row_data.append(cell_data)
    all_row_data.append(row_data)


# Create a DataFrame from the accumulated data
df = pd.DataFrame(all_row_data)

# Specify your desired CSV file path
csv_file_path = "soup.csv"

# Export the DataFrame to a CSV file
df.to_csv(csv_file_path, index=False, header=False)

df_transposed = df.T
df_transposed.columns = [
    Cash_Flow_Statement_MAP.get(col, col) for col in df_transposed.iloc[0]
]

df_transposed = df_transposed.drop(df_transposed.index[0])

Base = declarative_base()
engine = create_engine("sqlite:///database/stocks.db", echo=True)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


for index, row in df_transposed.iterrows():
    # Convert the row to a dictionary, mapping column names to values
    row_data = {column: value for column, value in zip(df_transposed.columns, row)}
    row_data["CompanyName"] = ticker
    # Optional: Convert specific columns to the correct data type
    # For example, converting 'PublicationDate' to a datetime.date object

    # Convert numeric values from string to float where necessary
    if "PublicationDate" in row_data:
        row_data["PublicationDate"] = row_data["PublicationDate"]

    # Dynamically convert numeric values from string to float
    for column, value in row_data.items():
        # Check if the value is not None and the column is not 'PublicationDate'
        if value is not None and column != "PublicationDate":
            try:
                # Attempt to convert to float; this assumes all other columns are numeric
                row_data[column] = float(value)
            except ValueError:
                # If conversion fails, keep the original value
                # This is useful for columns that are not numeric
                continue

    cash_flow_statement_record = CashFlowStatement(**row_data)
    # Add the instance to the session
    session.add(cash_flow_statement_record)

session.commit()

session.close()

# df_transposed.to_csv("test.csv", index=False, header=False)
