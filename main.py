#%% Import Sources & Required Libraries
from util import *
import os
import time

#%% Main Loop
if __name__ == "__main__":
    args = opts().parse()
    while args.mode == "plot":
        ts_class = time_series(args)
        os.system('cls')
        ts_class.update()
        ts_class.plot()
        time.sleep(30)
        if ts_class.now() > ts_class.pm8:
            break

    if args.mode == "check":
        tickers = ["BRP", "BRBR", "BILL", "ONEW", "SDGR",
                   "ZI", "DNB", "LMND", "NCNO", "RNLX",
                   "IBEX", "SITM", "XP", "VEL",
                   "REYN", "GAN", "ACI", "WMG", "VERX",
                   "VITL", "AUVI", "KBNT"]
        df = pd.DataFrame(columns=["ticker", "ratio", "interval"])
        df["ticker"] = tickers
        print(df.iloc[0,0])
        for i, t in enumerate(tickers):
            print(t + " performance:")
            check = statYahoo(t, profit=0.5, period=21)
            ratio, interval = check.compute()
            df.iloc[i, 0] = t
            df.iloc[i, 1] = ratio
            df.iloc[i, 2] = interval
        
        df.to_excel("performance.xlsx")