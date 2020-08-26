#%% Import Sources & Required Libraries
from util import *
import os

#%% Main Loop
if __name__ == "__main__":
    args = opts().parse()
    ts = time_series(args)
    while True:
        os.system('cls')
        ts.update()
        ts.plot()
        if ts.now() > ts.pm8:
            break
