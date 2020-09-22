#%% Import Required Libraries
import numpy as np
import pandas as pd
from alpha_vantage.timeseries import TimeSeries # Alphavantage Python API, $pip install alpha_vantage
import time
from datetime import datetime
import pytz # Python TimeZone
import argparse
import matplotlib.pyplot as plt
import mplfinance as mpf # matplotlib finance, $pip install --upgrade mplfinance
import yfinance as yf

#%% ArgumentParser
class opts():
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="alpha_vantage",
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        self.parser.add_argument("-m", "--mode", default="check", type=str, choices=["check", "plot"],
                                 dest="mode")
        self.parser.add_argument("-k", "--key", default="", type=str, dest="key")
        self.parser.add_argument("-t", "--ticker", default="", type=str, dest="ticker")
        self.parser.add_argument("-s", "--style", default="close_only", choices=["candle", "close_only"],
                                 type=str, dest="style")
        self.parser.add_argument("--interval", default="1min",
                                 choices=["15min", "5min", "15min", "30min", "60min"], type=str, dest="interval")
        self.parser.add_argument("--initial_size", default="compact", choices=["compact", "full"],
                                 type=str, dest="initial_size")
    
    def parse(self, args : str = None):
        if args == None:
            opt = self.parser.parse_args()
        else:
            opt = self.parser.parse_args(args)

        return opt

#%% Get TimeSeries Object
class time_series():
    def __init__(self, opt):
        super(time_series, self).__init__()
        self.key = opt.key
        self.ticker = opt.ticker
        self.style = opt.style
        self.interval = opt.interval
        self.output_size = opt.initial_size
        self.ts = TimeSeries(key=self.key, output_format='pandas')
        self.data, self.meta_data = self.ts.get_intraday(symbol=self.ticker, interval=self.interval,
                                                         outputsize=self.output_size)
        columns = {"1. open":"Open", "2. high":"High", "3. low":"Low", "4. close":"Close", "5. volume":"Volume"}
        self.tz = pytz.timezone("America/New_York")
        now = self.now()
        self.init_time = np.datetime64(now)
        self.today = self.date(self.init_time)
        self.am8 = self.today + np.timedelta64(8, 'h')
        self.op = self.today + np.timedelta64(9, 'h') + np.timedelta64(30, 'm')
        self.cl = self.today + np.timedelta64(16, 'h')
        self.pm8 = self.today + np.timedelta64(20, 'h')
        self.data.index.names = ["Date"]
        self.data.rename(columns=columns, inplace=True)
        today_data = self.data[self.data.index.values >= self.am8]
        if not len(today_data)==0:
            self.data = today_data

    def now(self):
        return datetime.strptime(str(datetime.now(self.tz)), '%Y-%m-%d %H:%M:%S.%f-04:00')

    def date(self, time : np.datetime64):
        return time.astype('datetime64[D]')

    def update(self):
        data, _ = self.ts.get_intraday(symbol=self.ticker, interval=self.interval,
                                       outputsize="compact")
        data = data[data.index.values >= self.am8]
        if not len(data)==0:
            self.data = data.combine_first(self.data)
        del data, _
        
    def plot(self):
        if self.style == "close_only":
            self._close_only()
        elif self.style == "candle":
            self._candle()
    
    def _candle(self):
        mc = mpf.make_marketcolors(up='orangered',down='turquoise',
                           edge='inherit',
                           wick='grey',
                           volume='in',
                           ohlc='i')
        s  = mpf.make_mpf_style(marketcolors=mc)
        kwargs = dict(type='candle',volume=True,figratio=(11,8),figscale=1)
        mpf.plot(self.data.iloc[::-1],**kwargs, style=s)
    
    def _close_only(self):
        self.data['Close'].plot()
        plt.title('Intraday Times Series for the {ticker} stock ({interval})'.format(
            ticker=self.ticker, interval=self.interval))
        plt.show()

class checkStrategy():
    def __init__(self, opts, ticker : str, profit : float = 0.5, period : int = 21):
        super(checkStrategy, self).__init__()
        self.ticker = ticker
        self.profit = profit
        self.period = np.timedelta64(period, "D")
        self.ts = TimeSeries(key=opts.key, output_format='pandas')
        self.data, self.meta_data = self.ts.get_intraday(symbol=self.ticker, interval="60min",
                                                         outputsize="full")
        columns = {"1. open":"Open", "2. high":"High", "3. low":"Low", "4. close":"Close", "5. volume":"Volume"}
        self.data.rename(columns=columns, inplace=True)
        self.enter_price = self.data.iloc[-1, 2]
        self.exit_price = self.enter_price
        self.interval = period
        self.ratio = profit

    def date(self, time):
        return np.datetime64(time).astype('datetime64[D]')

    def compute(self):
        enter_date = self.data.index[-1]
        enter_date = self.date(enter_date)

        exit_date = enter_date + np.timedelta64(21, 'D')
        exit_date_tomorrow = exit_date + np.timedelta64(1, "D")
        tmp = self.data[self.data.index >= exit_date]
        result = tmp[tmp.index < exit_date_tomorrow]
        self.exit_price = result["High"].argmax()
        self.interval = np.timedelta64(21, "D")

        over_profit = self.data[self.data["High"] >= self.enter_price * (1 + self.profit)]

        if not len(over_profit) == 0:
            self.exit_price = over_profit.iloc[-1, 1]
            self.revenue = self.exit_price - self.enter_price
            exit_date = over_profit.index[-1]
            exit_date = self.date(exit_date)
            self.interval = exit_date - enter_date

        self.ratio = (self.exit_price - self.enter_price) / self.enter_price

        return self.ratio, self.interval

class statYahoo():
    def __init__(self, ticker : str, profit : float = 0.5, period : int = 21):
        super(statYahoo, self).__init__()
        self.ticker = yf.Ticker(ticker)
        self.profit = profit
        self.period = np.timedelta64(period, "D")
        self.data = self.ticker.history(period="max")
        self.enter_price = self.data.iloc[0, 2]
        self.exit_price = self.enter_price
        self.interval = np.timedelta64(period, "D")

    def date(self, time):
        return np.datetime64(time).astype('datetime64[D]')

    def ratio(self):
        return (self.exit_price - self.enter_price) / self.enter_price

    def compute(self):
        enter_date = self.date(self.data.index[0])
        exit_date = enter_date + self.period
        result = self.data[self.data.index == exit_date]
        try:
            self.exit_price = result["High"].values[0]
        except:
            result = self.data[self.data.index == exit_date + np.timedelta64(1, "D")]
            self.exit_price = result["High"].values[0]
        self.interval = self.period

        over_profit = self.data[self.data["High"] >= self.enter_price * (1 + self.profit)]

        if not len(over_profit) == 0:
            date_over_profit = over_profit.index[0]
            if date_over_profit <= exit_date:            
                self.exit_price = over_profit.iloc[0, 1]
                self.revenue = self.exit_price - self.enter_price
                exit_date = over_profit.index[0]
                exit_date = self.date(exit_date)
                self.interval = exit_date - enter_date

        print("enter : $" + str(self.enter_price) + ", " + str(enter_date))
        print("exit : $" + str(self.exit_price) + ", " + str(exit_date))
        
        return self.ratio(), self.interval