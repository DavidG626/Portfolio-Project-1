import yfinance as yf

def debug_ticker_info(symbol):
    print(f"Debugging ticker info for {symbol}")
    ticker = yf.Ticker(symbol)
    
    # Print all available keys in ticker.info
    print("\nAll available keys in ticker.info:")
    print(list(ticker.info.keys()))
    
    # Try accessing commonly used properties
    print("\nTrying to access common properties:")
    properties = [
        'longName', 'longBusinessSummary', 'currentPrice', 'regularMarketPrice', 
        'fiftyTwoWeekHigh', 'fiftyTwoWeekLow', 'volume', 'marketCap', 'forwardPE'
    ]
    
    for prop in properties:
        try:
            value = ticker.info.get(prop, "Not found")
            print(f"{prop}: {value}")
        except Exception as e:
            print(f"{prop}: Error - {e}")
    
    # Check fast_info properties
    print("\nFast info properties:")
    try:
        fast_info = ticker.fast_info
        print(dir(fast_info))
    except Exception as e:
        print(f"Error accessing fast_info: {e}")

if __name__ == "__main__":
    # Test with a few different symbolsp
    for symbol in ["AAPL"]:
        debug_ticker_info(symbol)
        print("\n" + "="*50 + "\n")