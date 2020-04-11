from statsmodels.regression.rolling import RollingOLS
import statsmodels.api as sm
import numpy as np
import matplotlib.pyplot as plt
import json

def z_score(prices_a, prices_b):
    prices_a = sm.add_constant(prices_a)
    rolling_beta = RollingOLS(endog=prices_b, exog=prices_a, window=30).fit()
    prices_a = prices_a['subset_prices_a']
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

    # plt.figure(figsize=(15,7))
    # plt.plot(zscore_30_1)
    # plt.axhline(0, color='black')
    # plt.axhline(1.0, color='red', linestyle='--')
    # plt.axhline(-1.0, color='green', linestyle='--')
    # plt.legend(['Rolling Ratio z-Score', 'Mean', '+1', '-1'])
    # plt.show()

    return zscore_30_1.iloc[-1], hedge

def get_subset(ts_a, ts_b, end_index, sample_size):
    subset_a = ts_a[end_index-sample_size:end_index]
    subset_b = ts_b[end_index-sample_size:end_index]
    return subset_a, subset_b

def open_to_trading(current_trade):
    return len(current_trade) > 0

def calculate_wallet_delta(
    price_a,
    price_b,
    hedge,
    type
):
    if type == 'short':
        return price_b - hedge * price_a
    else:
        return price_a * hedge - price_b

def save_plot(balance, balances, pair):
    if balance > 0:
        plt.plot(balances)
        plt.title('Rolling Balance ('+pair+')')
        plt.xlabel('Passes')
        plt.ylabel('Balance')

        plt.draw()
        plt.savefig('backtest/results/'+pair+'.png')
        plt.clf()

def calculate_precentage_profit(
    current_trade,
    price_a,
    price_b
):
    hedge = current_trade['hedge']
    previous_a = current_trade['price_a']
    previous_b = current_trade['price_b']

    return (hedge*np.log(price_a) - np.log(price_b))-(hedge*np.log(previous_a) - np.log(previous_b))
    # diff_a = (np.log(price_a) - np.log(current_trade['price_a'])) * current_trade['hedge']
    # diff_b = np.log(price_b) - np.log(current_trade['price_b'])
    # return (diff_a + diff_b) * 100

def build_trade(price_a, price_b, hedge, type):
    print('opening_trade')
    return {
        'price_a': price_a,
        'price_b': price_b,
        'hedge': hedge,
        'type': type,
        'non_coint_count': 0
    }

def is_cointegrated(asset_a, asset_b):
    with open('processes/coint_results.json') as f:
        list = json.load(f)

        return asset_a+'|'+asset_b in list
