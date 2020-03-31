import numpy as np
import pandas as pd
import statsmodels.api as sm

def linregress(asset_a, asset_b):
    asset_a = sm.add_constant(asset_a)
    results = sm.OLS(asset_b, asset_a).fit()
    # asset_a = asset_a[:, 1]
    return results.params.iloc[1]

prices_a = pd.Series([1,3,2,4,3,5,4,6,5,7])
prices_b = pd.Series([2,6,4,8,6,10,8,12,10,14])

# returns_a = (np.log(prices_a) - np.log(prices_a).shift(1))[1:]
# returns_b = (np.log(prices_b) - np.log(prices_b).shift(1))[1:]
returns_a = prices_a.pct_change()[1:]
returns_b = prices_b.pct_change()[1:]

beta = linregress(prices_a, prices_b)

print beta

print prices_a * beta
