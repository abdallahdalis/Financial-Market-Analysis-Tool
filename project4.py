# MCS 275 Spring 2024 Project - Financial Market Analysis Tool
# Abdallah Dalis
# I am the sole author of this project, except where contributions of others
# are noted in README.md.

import sqlite3

from analysis import (analyze, load_prices, add_indicators, summary_stats,
                      forecast, garch_volatility)
from plotting import plot_overview

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

def print_analysis(conn, symbol, forecast_steps=5):
    """Print risk-return summary + forecast and show the overview chart."""
    ind, stats, fc = analyze(conn, symbol, forecast_steps=forecast_steps)

    print(f"\n=== {symbol} — time-series summary ===")
    print(f"  Observations:           {stats['observations']} "
          f"({stats['start']} → {stats['end']})")
    print(f"  Total return:           {stats['total_return']:+.2%}")
    print(f"  Annualized return:      {stats['annualized_return']:+.2%}")
    print(f"  Annualized volatility:  {stats['annualized_volatility']:.2%}")
    print(f"  Sharpe ratio (rf=0):    {stats['sharpe_ratio']:.2f}")
    print(f"  Max drawdown:           {stats['max_drawdown']:.2%}")

    print(f"\n  {forecast_steps}-day close forecast:")
    for d, v in fc.items():
        print(f"    {d.date()}  {v:.2f}")

    garch = garch_volatility(load_prices(conn, symbol), horizon=forecast_steps)
    if garch:
        print("\n  GARCH(1,1) conditional volatility (annualized):")
        print(f"    Latest:                 {garch['latest_annualized_vol']:.2%}")
        print(f"    {forecast_steps}-day-ahead forecast:    {garch['forecast_annualized_vol']:.2%}")

    plot_overview(ind, symbol, forecast=fc)

def main():
    """Main function to run the financial market analysis tool."""
    database = "stocks.db"
    conn = create_connection(database)
    if conn is None:
        print("Could not open database. Exiting.")
        return
    create_table(conn)

    while True:
        print("\nStock Analysis Tool")
        print("1. View Stock Chart (price, moving averages, Bollinger, volume)")
        print("2. Insert Stock Data")
        print("3. Update Stock Data")
        print("4. Delete Stock Data")
        print("5. Analyze (time-series stats + forecast)")
        print("6. Exit")
        choice = input("Enter choice: ")

        if choice == '1':
            while True:  # Keep looping until valid input is provided or user exits
                try:
                    symbol = input("Enter stock symbol: ").upper()
                    ind, _, fc = analyze(conn, symbol)
                    plot_overview(ind, symbol, forecast=fc)
                    break
                except ValueError as e:
                    print("Error:", e)
                    retry = input("Would you like to retry? (yes/no): ")
                    if retry.lower() != 'yes':
                        break
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
            try:
                symbol = input("Enter stock symbol: ").upper()
                print_analysis(conn, symbol)
            except ValueError as e:
                print("Error:", e)
        elif choice == '6':
            conn.close()
            print("Exiting Stock Analysis Tool.")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 6.")


if __name__ == "__main__":
    main()
