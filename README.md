# Financial Market Analysis Tool

MCS 275 Spring 2024 Project 4 by Abdallah Dalis

- This Project was customizable to my topic of choice with the approval of the Professor.


## Description

The Financial Market Analysis Tool is a Python program designed to analyze stock market data. The tool allows users to view stock charts, insert new stock data, update existing data, and delete data from a SQLite database. It leverages SQLite for data storage and Matplotlib for data visualization.

## How to test

1. Ensure you have Python installed on your system.
2. Run the program by executing the following command: `python3 project4.py`
3. Follow the on-screen menu to perform various actions:
   - To view a stock chart, enter option 1 and provide the stock symbol and plot type.
   - To insert new stock data, enter option 2 and follow the prompts to input data.
   - To update existing stock data, enter option 3 and provide the symbol, date, and new closing price.
   - To delete stock data, enter option 4 and provide the symbol and date.
   - To exit the program, enter option 5.

## Personal contribution

This idea and project is solely based on my personal contribution. With the help of multiple sources listed below

## Sources and credits

1. Patrick Ward. My TA reviewed an early prototype of the database and analysis tool  and helped me find and fix a troublesome bug related to the error if it was not inputted correctly. 
2. ChatGPT (general troubleshooting and addition to follow up responses if input was formatted incorrectly)


Feedback:
Nice project! It worked well in my testing, The main weak points were: 
* Entering a bunch of numbers on one line is a little inconvenient. I wish there was a way to do this with a HTML form or guided series of questions 
* I don't think the high, low, or volume are used in any way. It would be natural to add bars to the line plot showing the range over that trading day.  Still, very nice.
