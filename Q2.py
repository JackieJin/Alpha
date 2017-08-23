

import datetime as dt

import numpy as np
import pandas as pd

from diagnostics import performance, factor_utils

if __name__ == "__main__":
    prices = pd.DataFrame(np.random.randn(100,26), index = pd.date_range(end=dt.date.today(),periods=100), columns = list('ABCEDFGHIJKLMNOPQRSTUVWXYZ'))
    fr = factor_utils.compute_forward_returns(prices, [1, 5])
    fr.loc[:, 'factor'] = np.random.randn(2600)
    fr.loc[:, 'factor_quantile'] = factor_utils.quantize_factor(fr, 10)
    fr.sort_index(inplace=True)
    fr.loc[(slice(None), slice('A', 'D')), 'group'] = 'group1';
    fr.loc[(slice(None), slice('E', 'H')), 'group'] = 'group2';
    fr.loc[(slice(None), slice('H', 'Z')), 'group'] = 'group3';

    performance.mean_return_by_quantile(fr,False,True)
    performance.factor_information_coefficient(fr, True, True)


    fr1 = fr.loc[:,1].unstack()
    mr = factor_utils.aggregate_returns(fr1, 'M')
