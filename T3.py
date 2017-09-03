
import datetime as dt
import numpy as np
import pandas as pd



prices = pd.DataFrame(np.random.randn(100,3), index = pd.date_range(end=dt.date.today(),periods=100), columns = list('ABC'))
prices.ix[ prices.index[-1] + dt.timedelta(1), 'A'] = 3
prices.ix[ prices.index[-1] + dt.timedelta(1), ['A','B']] = np.random.rand(1,2)

#append
new = prices.ix[prices.index[-2:]+dt.timedelta(2),['A','B']]
new.ix[:] = np.random.rand(2,2)
prices.append(new)


#MultiIndex Dataframe
# construct from_product
index1 = pd.MultiIndex.from_product([pd.date_range(end = dt.date.today(), periods=10), list('AB')], names = ['date', 'asset'])
prices1 = pd.DataFrame(np.random.randn(20,1), index = index1, columns=['price'])

#construct from_array
index2 = pd.MultiIndex.from_arrays([list(pd.date_range(end = dt.date.today(), periods=5))*2,
                                    ['A'] * 5 +  ['B']*5], names = ['date', 'asset'] )

prices2 = pd.DataFrame(np.random.randn(10,1), index = index2, columns=['price'])
prices2.sort_index(inplace=True)

#append one row
prices2.ix[(prices2.index[-1][0]+ dt.timedelta(1), 'A'),:] =4

prices2.ix[(prices2.index[-1][0], 'B'),:] =5
prices2.ix[prices2.index[-4:],:]  = [6, 6,5,5]

#append  two rows
new = prices2.ix[pd.MultiIndex.from_arrays( [prices2.index[-2:] .get_level_values(0)  + dt.timedelta(1),
                                       prices2.index[-2:] .get_level_values(1)]),:
];
new.ix[:] =np.array([1,2]).reshape(2,1)
prices2.append(new)


new1 = prices2.ix[pd.MultiIndex.from_product([prices2.index[-1][0]+dt.timedelta(1), list('AB')], names = ['date', 'asset']),:]
new1.ix[:] = np.array([2,3]).reshape(2,1)
prices2.append(new1)