import sqlite3
print("database.py imported successfully")
def connect_to_db(db_file):
    """
    Establish a connection to the SQLite database.
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
        return None

def fetch_tickers(conn):
    """
    Fetch stock tickers from the database.
    """
    try:
        cur = conn.cursor()
        cur.execute("SELECT Ticker, Name FROM gpw_stocks_list")
        rows = cur.fetchall()
        return rows # Extracting the first element of each tuple
    except sqlite3.Error as e:
        print(e)
        return []

def close_connection(conn):
    """
    Close the connection to the database.
    """
    if conn:
        conn.close()
