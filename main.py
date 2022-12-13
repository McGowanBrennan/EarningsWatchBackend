import datetime
<<<<<<< Updated upstream
from flask_socketio import SocketIO
import websocket
import flask
import pandas as pd
from flask import Flask
=======

from supabase import create_client, Client
import flask
from flask import Flask, jsonify
>>>>>>> Stashed changes
from pandas_datareader import data
import finnhub
import yfinance as yf
from dotenv import load_dotenv
import os
<<<<<<< Updated upstream
from supabase import create_client, Client
=======
>>>>>>> Stashed changes
load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)
finnhub_client = finnhub.Client(api_key="ce8klkaad3i1v8pn82c0ce8klkaad3i1v8pn82cg")
app = Flask(__name__)


@app.route('/createEarningsForWeek')
def index():
    data = (finnhub_client.earnings_calendar(_from="2022-12-12", to="2022-12-16", symbol="", international=False))
    print(data)
    data_formatted = format_data(data.get("earningsCalendar"))
    for ticker in data_formatted:
        data = supabase.table("Earnings").insert({"ticker": ticker.ticker if ticker.ticker is not None else "",
                                                  "eps_est": ticker.eps_est if ticker.eps_est is not None else 0,
                                                  "rev_est": ticker.rev_est if ticker.rev_est is not None else 0,
                                                  "eps_act": ticker.eps_act if ticker.eps_act is not None else 0,
                                                  "rev_act": ticker.rev_act if ticker.rev_act is not None else 0,
                                                  "hour": ticker.hour if ticker.hour is not None else "",
                                                  "cap": ticker.cap if ticker.cap is not None else 0,
                                                  "date": ticker.date if ticker.date is not None else ""}).execute()
    return "hello wewda!"


@app.route("/sayHello")
def say_hello():
    return "hello"


@app.route("/getDailyImpliedMove")
def get_daily_implied_move():
    adbe = yf.Ticker("ADBE")
    print(adbe.options)
    print(adbe.option_chain(adbe.options[0]).calls)
    print(type(adbe.option_chain(adbe.options[0]).calls))
    df = adbe.option_chain(adbe.options[0]).calls
    print(df.head())
    return "OPTIONS"



@app.route("/getLargestEarnings")
def get_largest_earnings():
    compiled_earnings = {}
    for i in range(0, 2):
        day_dict = {}
        premarket = supabase.table("Earnings").select("*").eq("date", str(i)).eq("hour", "bmo").order("cap",
                                                                                                      desc=True).limit(
            10).execute()
        after_hours = supabase.table("Earnings").select("*").eq("date", str(i)).eq("hour", "amc").order("cap",
                                                                                                        desc=True).limit(
            10).execute()
        all_sessions = [premarket.data, after_hours.data]
        if premarket.data[0].get("date") == "0":
            day_dict["Monday"] = all_sessions
            compiled_earnings[0] = day_dict
        elif premarket.data[0].get("date") == "1":
            day_dict["Tuesday"] = all_sessions
            compiled_earnings[1] = day_dict
        elif premarket.data[0].get("date") == "2":
            day_dict["Wednesday"] = all_sessions
            compiled_earnings[2] = day_dict
        elif premarket.data[0].get("date") == "3":
            day_dict["Thursday"] = all_sessions
            compiled_earnings[3] = day_dict
        elif premarket.data[0].get("date") == "4":
            day_dict["Friday"] = all_sessions
            compiled_earnings[4] = day_dict
    response = jsonify(compiled_earnings)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


# @app.route("/getLargestEarningsQuotes")
# def get_quotes():
#     return on_message()




class EarningsData:
    def __init__(self, ticker, eps_est, rev_est, eps_act, rev_act, hour, cap, date):
        self.ticker = ticker
        self.eps_est = eps_est
        self.rev_est = rev_est
        self.eps_act = eps_act
        self.rev_act = rev_act
        self.hour = hour
        self.cap = cap
        self.date = date

    def __str__(self):
        return str(self.date) + str(self.ticker) + str(self.cap) + str(self.hour) + str(self.rev_act) + str(
            self.eps_act) + str(self.eps_est) + str(self.rev_est)


def format_data(ticker_info):
    list_of_ticker_objs = []
    tickers_seen = []
    ticker_data = []
    for ticker in ticker_info:
        if ticker.get("symbol") in tickers_seen:
            pass
        else:
            tickers_seen.append(ticker.get("symbol"))
            ticker_data.append(ticker)
    for ticker in ticker_data:
        print(ticker)
        ticker_data = yf.Ticker(ticker.get("symbol"))
        print(ticker_data.info.get("marketCap"))
        year, month, day = (int(x) for x in ticker.get("date").split('-'))
        day_of_week = datetime.date(year, month, day).weekday()
        obj = EarningsData(ticker.get("symbol"), ticker.get("epsEstimate"), ticker.get("revenueEstimate"),
                           ticker.get("epsActual"),
                           ticker.get("revenueActual"), ticker.get("hour"),
                           ticker_data.info.get("marketCap"),
                           day_of_week)
        if obj.cap is None:
            pass
        else:
            list_of_ticker_objs.append(obj)
    print(len(list_of_ticker_objs))
    return list_of_ticker_objs
