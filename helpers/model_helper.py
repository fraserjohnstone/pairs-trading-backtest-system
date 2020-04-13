from statsmodels.regression.rolling import RollingOLS
from statsmodels import regression
import statsmodels.api as sm
import numpy as np
import matplotlib.pyplot as plt
import json
import time
import pandas as pd

def simple_hedge(prices_a, prices_b):
    # returns_a = prices_a.pct_change()[1:]
    # returns_b = prices_b.pct_change()[1:]
    # returns_a.name = 'returns_a'
    # returns_b.name = 'returns_b'
    #
    # returns_a = sm.add_constant(returns_a)
    # model = regression.linear_model.OLS(returns_b,returns_a).fit()
    # returns_a = returns_a['returns_a']
    # return model.params[1]

    # prices_a = sm.add_constant(prices_a)
    # model = regression.linear_model.OLS(prices_b, prices_a).fit()
    # prices_a = prices_a['subset_prices_a']
    # return model.params[1]
    return (prices_a/prices_b).iloc[-1]

def simple_zscore(spreads):
    return (spreads.iloc[-1] - spreads.mean())/spreads.std()

def simple_spreads(prices_a, prices_b, hedge):
    # returns_a = prices_a.pct_change()[1:]
    # returns_b = prices_b.pct_change()[1:]

    # spreads = np.log(returns_b) - hedge * np.log(returns_a)
    spreads = np.log(prices_b) - np.log(prices_a)
    spreads.name = 'spreads'

    return spreads

def get_subset(ts_a, ts_b, end_index, sample_size):
    subset_a = ts_a[end_index-sample_size:end_index]
    subset_b = ts_b[end_index-sample_size:end_index]
    return subset_a, subset_b

def currently_trading(current_trade):
    return len(current_trade) > 0

# def save_plot(wallet, pair):
#     if wallet.holdings['btc'] > 100.0:
#         plt.plot(balances)
#         plt.title('Rolling Balance ('+pair+')')
#         plt.xlabel('Passes')
#         plt.ylabel('Balance')
#
#         plt.draw()
#         plt.savefig('results/'+pair+'.png')
#         plt.clf()

# def calculate_profit(
#     current_trade
# ):
#     return spread-current_trade['spread']
    # hedge = current_trade['hedge']
    # previous_a = current_trade['price_a']
    # previous_b = current_trade['price_b']
    #
    # return (hedge*np.log(price_a) - np.log(price_b))-(hedge*np.log(previous_a) - np.log(previous_b))
    # return (np.log(price_a) - hedge*np.log(price_b))-(np.log(previous_a) - hedge*np.log(previous_b))

def trade_quantity_btc():
    return 1.0

def trade_quantity_asset(price):
    return trade_quantity_btc()/price

def build_trade(price_a, price_b, hedge, type):
    quantity_a = trade_quantity_asset(price_a)
    quantity_b = trade_quantity_asset(price_b)

    return {
        'price_a': price_a,
        'price_b': price_b,
        'quantity_a': quantity_a,
        'quantity_b': quantity_b,
        'hedge': hedge,
        'type': type,
        'non_coint_count': 0
    }

def is_cointegrated(asset_a, asset_b):
    with open('processes/coint_results.json') as f:
        list = json.load(f)

        return asset_a+'|'+asset_b in list

def generate_coint_series(samples=10000, a_shift=20, b_shift=10):
    noise = np.random.normal(0, 1, samples)

    prices_a = [a_shift]

    for i in range(1, samples):
        new_price = prices_a[i-1] + np.random.normal(0, 1, 1)[0]
        while new_price <= 10:
            new_price = prices_a[i-1] + np.random.normal(0, 1, 1)[0]
        prices_a.append(new_price)

    prices_a = pd.Series(prices_a)
    prices_b = prices_a + b_shift + noise

    return prices_a, prices_b

def display_coint_series(samples=100, b_shift=0):
    prices_a, prices_b = generate_coint_series(samples=samples, b_shift=b_shift)

    plt.plot(prices_a)
    plt.plot(prices_b)
    plt.show()
