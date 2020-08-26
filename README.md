# nasdaq_realtime_stocks
 Get real-time nasdaq stocks data via alphavantage API

# Installation
**Clone the repository
"""
$git clone https://github.com/bigbreadguy/nasdaq_realtime_stocks.git
"""<br/>
or github desktop and other methods also works

**Install all requirements
"""
$conda install -c anaconda numpy pandas matplotlib
"""<br/>
"""
$conda install -c conda-forge easydict
"""<br/>
"""
$pip install alpha_vantage
"""<br/>
"""
$pip install --upgrade mplfinance
"""<br/>

# Usage
KEY : alphavantage API key, get the key from here https://www.alphavantage.co/support/#api-key<br/>
TICKER : symbol that represents target stock (ex: AAPL for Apple Inc. Common Stock)<br/>

**Run main.py
"""
python main.py [-k, --key KEY] [-t, --ticker TICKER]
               [-s, --style {candle,close_only}]
               [--interval {15min,5min,15min,30min,60min}]
               [--initial_size {compact,full}]
"""
**Open realtime_display.ipynb
Input proper values into the easydict object and run
