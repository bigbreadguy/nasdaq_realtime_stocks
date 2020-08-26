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

#%% ArgumentParser
class opts():
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="alpha_vantage",
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
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
        self.data.index.names = ["Date"]
        self.data.rename(columns=columns, inplace=True)
        self.tz = pytz.timezone("America/New_York")
        now = self.now()
        self.init_time = np.datetime64(now)
        self.today = self.date(self.init_time)
        self.am8 = self.today + np.timedelta64(8, 'h')
        self.op = self.today + np.timedelta64(9, 'h') + np.timedelta64(30, 'm')
        self.cl = self.today + np.timedelta64(16, 'h')
        self.pm8 = self.today + np.timedelta64(20, 'h')

    def now(self):
        return datetime.strptime(str(datetime.now(self.tz)), '%Y-%m-%d %H:%M:%S.%f-04:00')

    def date(self, time : np.datetime64):
        return time.astype('datetime64[D]')

    def update(self):
        data, _ = self.ts.get_intraday(symbol=self.ticker, interval=self.interval,
                                       outputsize="compact")
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