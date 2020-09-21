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
        tickers = ["SDGR"]

        for t in tickers:
            check = checkStrategy(args, t)
            ratio, interval = check.compute()
            print(t + " performance:")
            print("profit rate : " + str(ratio))
            print("holding interval : " + str(interval))