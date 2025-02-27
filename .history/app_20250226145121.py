from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import yfinance as yf
# import pandas as pd
import plotly.graph_objects as go
import plotly
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'asdfasdfasdf') 


# Landing Page
@app.route('/')
def landing_page():
   return render_template('landing.html')  # Render the landing.html template


# function to connect to the database
def connect_db():
   return sqlite3.connect('database.db')




# create database
def create_tables():
   with connect_db() as conn:
       cursor = conn.cursor()
       #creates users table
       cursor.execute('''
                       CREATE TABLE IF NOT EXISTS users (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       username TEXT UNIQUE NOT NULL,
                       email TEXT UNIQUE NOT NULL,
                       password TEXT NOT NULL
                       )
                       ''')
create_tables()
# Register Route
@app.route('/register', methods=['POST'])
def register():
   username = request.form.get('username')
   email = request.form.get('email')
   password = request.form.get('password')


   # hash the password before storing it in the database
   hashed_password = generate_password_hash(password)
  
   #add user to the db
   with connect_db() as conn:
       cursor = conn.cursor()
      
       # Fetch existing user before executing the SELECT query
       cursor.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, email,))
       existing_user = cursor.fetchone()
      
       # Check if username or email already exists in db
       if existing_user:
           # If the username or email already exists, handle the error accordingly
           reg_error_message = "Username or email already exists."
           return render_template('landing.html', reg_error_message=reg_error_message)
  
       # If username and email are unique, insert into db
       cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, hashed_password,))
       # commit transaction
       conn.commit()
      
   return redirect('/')



# Login Route
@app.route('/login', methods=['POST'])
def login():
   login_username = request.form.get('login_username')
   login_password = request.form.get('login_password')

# retrieve user from the database based on the provided username
   with connect_db() as conn:
       cursor = conn.cursor()
       cursor.execute('SELECT * FROM users WHERE username = ?', (login_username,))
       user = cursor.fetchone()
  
   if user and check_password_hash(user[3], login_password,):
       # if the user exists and the password match, sets session
       session['username'] = login_username
       session['password'] = login_password
       return redirect('/dashboard')
   else:
      
       # if the user doesn't exist or the password is incorrect, display an error message
       login_error_message = "Invalid username or password"
       return render_template('landing.html', login_error_message=login_error_message)

      


  # Logout Route
@app.route('/logout', methods=['GET', 'POST'])
def logout():
   # Clear the session to log the user out
   session.clear()
   # Redirect the user to the landing page
   return redirect(url_for('landing_page'))


# overview Route
@app.route('/dashboard')
def dashboard():
   if 'username' in session:
       
       return render_template('overview.html', username=session['username'])
   else:
       return redirect(url_for('register'))


#input for ticker overview.html
@app.route('/process_form', methods=['POST'])
def process_form():
   ticker_symbol = request.form.get('ticker')
   if ticker_symbol:
       ticker = yf.Ticker(ticker_symbol)
       session['ticker_symbol'] = ticker_symbol
       return index()
   else:
       error_message = "Please Enter a Ticker Symbol"
       return render_template('overview.html', error_message=error_message)


@app.route('/overview')
def index():
    if 'username' in session:
        if 'ticker_symbol' in session:
            ticker_symbol = session['ticker_symbol']
            if not ticker_symbol:
                error_message = "Please Enter a Valid Tickerl"
                return render_template('overview.html', error_message=error_message)
                
            try:
                ticker = yf.Ticker(ticker_symbol)
                
                # Use fast_info instead of info for basic data
                fast_info = ticker.fast_info
                
                # Get company info 
                try:
                    company_info = ticker.info
                    company_name = company_info.get('longName', ticker_symbol.upper())
                    about = company_info.get('longBusinessSummary', 'No company description available.')
                except:
                    company_name = ticker_symbol.upper()
                    about = 'Unable to retrieve company description.'
                
                # Use fast_info for pricing data
                stock_price = '${:.2f}'.format(fast_info.last_price) if hasattr(fast_info, 'last_price') else 'N/A'
                fifty_two_week_high = '${:.2f}'.format(fast_info.year_high) if hasattr(fast_info, 'year_high') else 'N/A'
                fifty_two_week_low = '${:.2f}'.format(fast_info.year_low) if hasattr(fast_info, 'year_low') else 'N/A'
                volume = '{:,}'.format(fast_info.last_volume) if hasattr(fast_info, 'last_volume') else 'N/A'
                market_cap = '${:,.2f}'.format(fast_info.market_cap) if hasattr(fast_info, 'market_cap') else 'N/A'
                
                # Forward PE 
                try:
                    forward_PE = '{:.0f}'.format(ticker.info.get('forwardPE', 0)) if 'forwardPE' in ticker.info else 'N/A'
                except:
                    forward_PE = 'N/A'

                # Get news
                try:
                    news_data = ticker.news
                    current_news = [{'title': news_item['title'], 'link': news_item['link']} for news_item in news_data[:20]]
                except:
                    current_news = []
                
                return render_template('overview.html', 
                                      about=about, 
                                      company_name=company_name, 
                                      stock_price=stock_price,
                                      fifty_two_week_high=fifty_two_week_high, 
                                      fifty_two_week_low=fifty_two_week_low,
                                      volume=volume, 
                                      market_cap=market_cap, 
                                      forward_PE=forward_PE, 
                                      current_news=current_news, 
                                      ticker_symbol=ticker_symbol)
            
                                      return render_
            
        
    

  #income_statement.html route
@app.route('/income_statement')
def fetch_income_statement():
   ticker_symbol = session.get('ticker_symbol')
   if ticker_symbol:
       ticker = yf.Ticker(ticker_symbol)
       try:
           company_name = ticker.info['longName']
           income_statement = ticker.financials
           income_statement_clean = income_statement.dropna()
           income_statement_clean = income_statement.to_html()
      
           return render_template('income_statement.html', income_statement_clean=income_statement_clean, company_name=company_name)
       except KeyError:
           error_message = "Please Enter a Valid Ticker"
           return render_template('overview.html', error_message=error_message)
   else:
       return render_template('income_statement.html')



# For /cashflow route
@app.route('/cashflow')
def fetch_cashflow():
    ticker_symbol = session.get('ticker_symbol')
    if ticker_symbol:
        ticker = yf.Ticker(ticker_symbol)
        try:
            company_name = ticker.info['longName']
            cashflow_data = ticker.cashflow
            cashflow_data_clean = cashflow_data.dropna()
            cashflow_data_clean = cashflow_data.to_html()
       
            return render_template('cashflow.html', cashflow_data_clean=cashflow_data_clean, company_name=company_name)
        except KeyError:
            error_message = "Please Enter a Valid Ticker"
            return render_template('overview.html', error_message=error_message)
        except Exception as e:
            error_message = "Please Enter a Valid Ticker"
            return render_template('overview.html', error_message=error_message)
    else:
        return render_template('cashflow.html')  


#balance_sheet.html route
@app.route('/balance_sheet')
def fetch_balance_sheet():
   ticker_symbol = session.get('ticker_symbol')
   if ticker_symbol:
       ticker = yf.Ticker(ticker_symbol)
       try:
           company_name = ticker.info['longName']
           balance_sheet = ticker.balancesheet
           balance_sheet_clean = balance_sheet.dropna()
           balance_sheet_clean = balance_sheet.to_html()
      
           return render_template('balancesheet.html', balance_sheet_clean = balance_sheet_clean, company_name=company_name)
       except KeyError:
           error_message = "Please Enter a Valid Ticker"
           return render_template('overview.html', error_message=error_message)






#charts.html route
@app.route('/charts')
def fetch_charts():
   ticker_symbol = session.get('ticker_symbol')
   if ticker_symbol:


    ticker = yf.Ticker(ticker_symbol)
    try:
           company_name = ticker.info['longName']
           df = ticker.history(period='6mo')
           fig = go.Figure(data=[go.Candlestick(x=df.index,
                                               open=df['Open'],
                                               high=df['High'],
                                               low=df['Low'],
                                               close=df['Close'])])
          
           fig.update_layout(title=f"Candlestick Chart for {company_name}",
                                                          
                           width=1300,
                           height=600,
                           xaxis_title='Date',
                           yaxis_title='Price',
                           plot_bgcolor='antique white', 
                           paper_bgcolor='antique white')
          
           candlestick_chart = fig.to_html()
           return render_template('charts.html', candlestick_chart=candlestick_chart,
                                               company_name=company_name)
    except KeyError:
        error_message = "Please Enter a Valid Ticker"
        return render_template('overview.html', error_message=error_message)




#vix chart route
@app.route('/vix_charts')
def fetch_vix():
    vix_ticker = "^VIX"
    if vix_ticker:
       ticker = yf.Ticker(vix_ticker)
       df = ticker.history(period='6mo')
      
       fig = go.Figure(data=[go.Candlestick(x=df.index,
                                            open=df['Open'],
                                            high=df['High'],
                                            low=df['Low'],
                                            close=df['Close'])])


       fig.update_layout(title="Candlestick Chart for VIX",
                        
                         width=1300,
                         height=600,
                         xaxis_title='Date',
                         yaxis_title='Price',
                         plot_bgcolor='antique white', 
                         paper_bgcolor='antique white') 
       vix_candlestick_chart = fig.to_html()
       return render_template('vix_chart.html', vix_candlestick_chart=vix_candlestick_chart)








if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5501))
    app.run(host='0.0.0.0', port=port, debug=False)
