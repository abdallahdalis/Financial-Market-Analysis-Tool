# MCS 275 Spring 2024 Project - Financial Market Analysis Tool
# Abdallah Dalis
# I am the sole author of this project, except where contributions of others
# are noted in README.md.

import sqlite3
import matplotlib.pyplot as plt
import numpy as np

def create_connection(db_file):
    """Create a database connection to the SQLite database specified by db_file."""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print("SQLite DB Version:", sqlite3.version)
    except Exception as e:
        print(e)
    return conn

def create_table(conn):
    """Create a stock table if it doesn't already exist."""
    try:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS stocks (
                date text,
                symbol text,
                open real,
                high real,
                low real,
                close real,
                volume integer
            )
        ''')
        conn.commit()
    except Exception as e:
        print("Error creating table:", e)

def insert_data(conn, date, symbol, open_price, high, low, close, volume):
    """Insert new stock data into the stocks table."""
    try:
        c = conn.cursor()
        c.execute('''
            INSERT INTO stocks (date, symbol, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (date, symbol, open_price, high, low, close, volume))
        conn.commit()
    except Exception as e:
        print("Error inserting data:", e)

def update_data(conn, symbol, date, close):
    """Update the closing price for a given stock on a specific date."""
    try:
        c = conn.cursor()
        c.execute('''
            UPDATE stocks
            SET close = ?
            WHERE symbol = ? AND date = ?
        ''', (close, symbol, date))
        conn.commit()
    except Exception as e:
        print("Error updating data:", e)

def delete_data(conn, symbol, date):
    """Delete stock data for a given symbol on a specific date."""
    try:
        c = conn.cursor()
        c.execute('''
            DELETE FROM stocks
            WHERE symbol = ? AND date = ?
        ''', (symbol, date))
        conn.commit()
    except Exception as e:
        print("Error deleting data:", e)

def fetch_data(conn, symbol):
    """Fetch all stock data for a given symbol."""
    c = conn.cursor()
    c.execute('SELECT * FROM stocks WHERE symbol = ?', (symbol,))
    return c.fetchall()

def search(self, key):
        """Search for a node by key."""
        if key == self.key:
            return self.data
        elif key < self.key and self.left:
            return self.left.search(key)
        elif key > self.key and self.right:
            return self.right.search(key)
        return None    

def plot_data(data, plot_type='line'):
    """Plot stock data using Matplotlib. Supports 'line' and 'bar' plot types."""
    dates = [x[0] for x in data]
    prices = [x[5] for x in data]  # Close prices
    plt.figure(figsize=(10, 5))
    if plot_type == 'line':
        plt.plot(dates, prices, marker='o')
    elif plot_type == 'bar':
        plt.bar(dates, prices)
    plt.title('Stock Price Over Time')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.grid(True)
    plt.show()

def main():
    """Main function to run the financial market analysis tool."""
    database = "stocks.db"
    conn = create_connection(database)
    create_table(conn)

    while True:
        print("\nStock Analysis Tool")
        print("1. View Stock Chart")
        print("2. Insert Stock Data")
        print("3. Update Stock Data")
        print("4. Delete Stock Data")
        print("5. Exit")
        choice = input("Enter choice: ")

## Function written by ChatGPT
        if choice == '1':
            while True:  # Keep looping until valid input is provided or user exits
                try:
                    symbol = input("Enter stock symbol: ")
                    data = fetch_data(conn, symbol)
                    if not data:
                        raise ValueError(f"Stock symbol '{symbol}' not found in the database.")
                    plot_type = input("Enter plot type (line/bar): ")
                    plot_data(data, plot_type)
                    break  # Exit the loop if plotting is successful
                except ValueError as e:
                    print("Error:", e)
                    retry = input("Would you like to retry? (yes/no): ")
                    if retry.lower() != 'yes':
                        break  # Exit the loop if user chooses not to retry
        elif choice == '2':
            while True:  # Keep looping until valid input is provided
                try:
                    print("Enter stock data in the following format:")
                    print("date symbol open high low close volume")
                    data_input = input("Example: 2024-04-25 ABC 100.0 110.0 90.0 105.0 10000\n").split()
                    if len(data_input) != 7:
                        raise ValueError("Invalid input format. Please provide all required fields.")
                    date, symbol, open_price, high, low, close, volume = data_input
                    insert_data(conn, date, symbol, float(open_price), float(high), float(low), float(close), int(volume))
                    print("Data inserted successfully.")
                    break  # Exit the loop if insertion is successful
                except ValueError as e:
                    print("Error:", e)
        elif choice == '3':
            while True:  # Keep looping until valid input is provided or user exits
                try:
                    print("Enter stock update data in the following format:")
                    print("symbol date new_close_price")
                    data_input = input("Example: ABC 2024-04-25 105.0\n").split()
                    if len(data_input) != 3:
                        raise ValueError("Invalid input format. Please provide all required fields.")
                    symbol, date, close = data_input
                    update_data(conn, symbol, date, float(close))
                    print("Data updated successfully.")
                    break  # Exit the loop if update is successful
                except ValueError as e:
                    print("Error:", e)
                    retry = input("Would you like to retry? (yes/no): ")
                    if retry.lower() != 'yes':
                        break  # Exit the loop if user chooses not to retry
        elif choice == '4':
            while True:  # Keep looping until valid input is provided or user exits
                try:
                    print("Enter stock data to delete in the following format:")
                    print("symbol date")
                    data_input = input("Example: ABC 2024-04-25\n").split()
                    if len(data_input) != 2:
                        raise ValueError("Invalid input format. Please provide all required fields.")
                    symbol, date = data_input
                    delete_data(conn, symbol, date)
                    print("Data deleted successfully.")
                    break  # Exit the loop if deletion is successful
                except ValueError as e:
                    print("Error:", e)
                    retry = input("Would you like to retry? (yes/no): ")
                    if retry.lower() != 'yes':
                        break  # Exit the loop if user chooses not to retry
        elif choice == '5':
            conn.close() # type: ignore
            print("Exiting Stock Analysis Tool.")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 5.")


if __name__ == "__main__":
    main()
