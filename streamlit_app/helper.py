# Import path
# Import datetime
import datetime as dt
from pathlib import Path

# Import pandas
import pandas as pd

# Import yfinance
import yfinance as yf

# Import the required libraries
from statsmodels.tsa.ar_model import AutoReg


# Create function to fetch stock name and id
def fetch_stocks():
    # Load the data
    df = pd.read_csv(Path.cwd().parent.parent / "data" / "equity_issuers.csv")

    # Filter the data
    df = df[["Security Code", "Issuer Name"]]

    # Create a dictionary
    stock_dict = dict(zip(df["Security Code"], df["Issuer Name"]))

    # Return the dictionary
    return stock_dict


# Create function to fetch periods and intervals
def fetch_periods_intervals():
    # Create dictionary for periods and intervals
    periods = {
        "1d": ["1m", "2m", "5m", "15m", "30m", "60m", "90m"],
        "5d": ["1m", "2m", "5m", "15m", "30m", "60m", "90m"],
        "1mo": ["30m", "60m", "90m", "1d"],
        "3mo": ["1d", "5d", "1wk", "1mo"],
        "6mo": ["1d", "5d", "1wk", "1mo"],
        "1y": ["1d", "5d", "1wk", "1mo"],
        "2y": ["1d", "5d", "1wk", "1mo"],
        "5y": ["1d", "5d", "1wk", "1mo"],
        "10y": ["1d", "5d", "1wk", "1mo"],
        "max": ["1d", "5d", "1wk", "1mo"],
    }

    # Return the dictionary
    return periods


# Function to fetch the stock info
def fetch_stock_info(stock_ticker):
    # Pull the data for the first security
    stock_data = yf.Ticker(stock_ticker)

    # Extract full of the stock
    stock_data_info = stock_data.info

    # Extract only the important information
    stock_data_info = {
        "Basic Information": {
            "symbol": stock_data_info["symbol"],
            "longName": stock_data_info["longName"],
            "currency": stock_data_info["currency"],
            "exchange": stock_data_info["exchange"],
        },
        "Market Data": {
            "currentPrice": stock_data_info["currentPrice"],
            "previousClose": stock_data_info["previousClose"],
            "open": stock_data_info["open"],
            "dayLow": stock_data_info["dayLow"],
            "dayHigh": stock_data_info["dayHigh"],
            "regularMarketPreviousClose": stock_data_info["regularMarketPreviousClose"],
            "regularMarketOpen": stock_data_info["regularMarketOpen"],
            "regularMarketDayLow": stock_data_info["regularMarketDayLow"],
            "regularMarketDayHigh": stock_data_info["regularMarketDayHigh"],
            "fiftyTwoWeekLow": stock_data_info["fiftyTwoWeekLow"],
            "fiftyTwoWeekHigh": stock_data_info["fiftyTwoWeekHigh"],
            "fiftyDayAverage": stock_data_info["fiftyDayAverage"],
            "twoHundredDayAverage": stock_data_info["twoHundredDayAverage"],
        },
        "Volume and Shares": {
            "volume": stock_data_info["volume"],
            "regularMarketVolume": stock_data_info["regularMarketVolume"],
            "averageVolume": stock_data_info["averageVolume"],
            "averageVolume10days": stock_data_info["averageVolume10days"],
            "averageDailyVolume10Day": stock_data_info["averageDailyVolume10Day"],
            "sharesOutstanding": stock_data_info["sharesOutstanding"],
            "impliedSharesOutstanding": stock_data_info["impliedSharesOutstanding"],
            "floatShares": stock_data_info["floatShares"],
        },
        "Dividends and Yield": {
            "dividendRate": stock_data_info["dividendRate"],
            "dividendYield": stock_data_info["dividendYield"],
            "payoutRatio": stock_data_info["payoutRatio"],
        },
        "Valuation and Ratios": {
            "marketCap": stock_data_info["marketCap"],
            "enterpriseValue": stock_data_info["enterpriseValue"],
            "priceToBook": stock_data_info["priceToBook"],
            "debtToEquity": stock_data_info["debtToEquity"],
            "grossMargins": stock_data_info["grossMargins"],
            "profitMargins": stock_data_info["profitMargins"],
        },
        "Financial Performance": {
            "totalRevenue": stock_data_info["totalRevenue"],
            "revenuePerShare": stock_data_info["revenuePerShare"],
            "totalCash": stock_data_info["totalCash"],
            "totalCashPerShare": stock_data_info["totalCashPerShare"],
            "totalDebt": stock_data_info["totalDebt"],
            "earningsGrowth": stock_data_info["earningsGrowth"],
            "revenueGrowth": stock_data_info["revenueGrowth"],
            "returnOnAssets": stock_data_info["returnOnAssets"],
            "returnOnEquity": stock_data_info["returnOnEquity"],
        },
        "Cash Flow": {
            "freeCashflow": stock_data_info["freeCashflow"],
            "operatingCashflow": stock_data_info["operatingCashflow"],
        },
        "Analyst Targets": {
            "targetHighPrice": stock_data_info["targetHighPrice"],
            "targetLowPrice": stock_data_info["targetLowPrice"],
            "targetMeanPrice": stock_data_info["targetMeanPrice"],
            "targetMedianPrice": stock_data_info["targetMedianPrice"],
        },
    }

    # Return the stock data
    return stock_data_info


# Function to fetch the stock history
def fetch_stock_history(stock_ticker, period, interval):
    # Pull the data for the first security
    stock_data = yf.Ticker(stock_ticker)

    # Extract full of the stock
    stock_data_history = stock_data.history(period=period, interval=interval)[
        ["Open", "High", "Low", "Close"]
    ]

    # Return the stock data
    return stock_data_history


# Function to generate the stock prediction
def generate_stock_prediction(stock_ticker):
    # Try to generate the predictions
    try:
        # Pull the data for the first security
        stock_data = yf.Ticker(stock_ticker)

        # Extract the data for last 1yr with 1d interval
        stock_data_hist = stock_data.history(period="2y", interval="1d")

        # Clean the data for to keep only the required columns
        stock_data_close = stock_data_hist[["Close"]]

        # Change frequency to day
        stock_data_close = stock_data_close.asfreq("D", method="ffill")

        # Fill missing values
        stock_data_close = stock_data_close.fillna(method="ffill")

        # Define training and testing area
        train_df = stock_data_close.iloc[: int(len(stock_data_close) * 0.9) + 1]  # 90%
        test_df = stock_data_close.iloc[int(len(stock_data_close) * 0.9) :]  # 10%

        # Define training model
        model = AutoReg(train_df["Close"], 250).fit(cov_type="HC0")

        # Predict data for test data
        predictions = model.predict(
            start=test_df.index[0], end=test_df.index[-1], dynamic=True
        )

        # Predict 90 days into the future
        forecast = model.predict(
            start=test_df.index[0],
            end=test_df.index[-1] + dt.timedelta(days=90),
            dynamic=True,
        )

        # Return the required data
        return train_df, test_df, forecast, predictions

    # If error occurs
    except:
        # Return None
        return None
