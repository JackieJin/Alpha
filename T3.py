
import datetime as dt
import numpy as np
import pandas as pd



prices = pd.DataFrame(np.random.randn(100,3), index = pd.date_range(end=dt.date.today(),periods=100), columns = list('ABC'))
prices.loc[ prices.index[-1] + dt.timedelta(1), 'A'] = 3
prices.loc[ prices.index[-1] + dt.timedelta(1), ['A','B']] = np.random.rand(1,2)

#append
new = pd.DataFrame(index=prices.index[-2:]+dt.timedelta(2),columns = ['A','B'])
new.loc[:] = np.random.rand(2,2)
prices = prices.append(new)


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
prices2.loc[(prices2.index[-1][0]+ dt.timedelta(1), 'A'),:] =4

prices2.loc[(prices2.index[-1][0], 'B'),:] =5
prices2.loc[prices2.index[-4:],:]  = [6, 6,5,5]

#append  two rows
new = pd.DataFrame(index = pd.MultiIndex.from_arrays( [prices2.index[-2:] .get_level_values(0)  + dt.timedelta(1),
                                       prices2.index[-2:] .get_level_values(1)]), columns = prices2.columns
)
new.loc[:] =np.array([1,2]).reshape(2,1)
prices2 = prices2.append(new)


pos = {'A': 0.4, 'B': 0.6}
new1 = pd.DataFrame(np.array(list(pos.values())).reshape(2,1), columns=prices2.columns,  index = pd.MultiIndex.from_product([[prices2.index[-1][0]+dt.timedelta(1)], list(pos.keys())], names = ['date', 'asset']))
prices2 = prices2.append(new1)



