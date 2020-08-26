#%% Import Sources & Required Libraries
from util import *
import os
import time

#%% Main Loop
if __name__ == "__main__":
    args = opts().parse()
    ts_class = time_series(args)
    while True:
        os.system('cls')
        ts_class.update()
        ts_class.plot()
        time.sleep(30)
        if ts_class.now() > ts_class.pm8:
            break
