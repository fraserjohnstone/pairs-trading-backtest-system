from statsmodels.regression.rolling import RollingOLS
import statsmodels.api as sm
import matplotlib.pyplot as plt

def z_score(prices_a, prices_b):
    # prices_a = sm.add_constant(prices_a)
    rolling_beta = RollingOLS(endog=prices_b, exog=prices_a, window=30).fit()
    # prices_a = prices_a['prices_a']
    hedge = rolling_beta.params['subset_prices_a'].iloc[-1]

    spreads = prices_b - rolling_beta.params['subset_prices_a'] * prices_a
    spreads.name = 'spreads'

    spreads_mavg_1 = spreads.rolling(1).mean()
    spreads_mavg_1.name = 'spreads 1d mavg'

    spreads_mavg30 = spreads.rolling(30).mean()
    spreads_mavg30.name = 'spreads 30d mavg'

    std_30 = spreads.rolling(30).std()
    std_30.name = 'std 30d'

    zscore_30_1 = (spreads_mavg_1 - spreads_mavg30)/std_30
    zscore_30_1.name = 'z-score'

    return zscore_30_1.iloc[-1], hedge

def get_subset(ts_a, ts_b, end_index, sample_size):
    subset_a = ts_a[end_index-sample_size:end_index]
    subset_b = ts_b[end_index-sample_size:end_index]
    return subset_a, subset_b
