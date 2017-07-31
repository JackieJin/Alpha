
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def run ():
    a = np.array([[1, 3], [2, 4]])
    b = np.array([[1, 3], [2, 3]])
    c = a + b
    d = [1, 2, 3, 4]
    ts = pd.Series(np.random.randn(1000), index=pd.date_range('1/1/2000', periods=1000))

    dates = pd.date_range('20130101', periods=6)
    df = pd.DataFrame(np.random.randn(6, 4), index=dates, columns=list('ABCD'))
    # ts.plot()
    # df.plot()
    # plt.show()

    x = np.arange(100)
    y = 2 * x + np.random.randn(100)

if __name__ == '__main__':
    run()
