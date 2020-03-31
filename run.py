import numpy as np
import pandas as pd
import math
import statsmodels.api as sm
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import coint
import random

def get_hedge_ratio(log_returns_a, log_returns_b):
    log_returns_a = sm.add_constant(log_returns_a)
    results = sm.OLS(log_returns_b, log_returns_a).fit()
    log_returns_a = log_returns_a
    return results.params[1]

def get_spreads(prices_a, prices_b, hedge_ratio):
    spreads = hedge_ratio * np.log(prices_a) - np.log(prices_b)
    return spreads

def generate_coint_series(period=100, a_shift=10, b_shift=5):
    noise = np.random.normal(0, 1, period)

    prices_a = [a_shift]

    for i in range(1, period):
        new_price = prices_a[i-1] + np.random.normal(0, 1, 1)[0]
        while new_price <= 10:
            new_price = prices_a[i-1] + np.random.normal(0, 1, 1)[0]
        prices_a.append(new_price)

    prices_a = pd.Series(prices_a)
    prices_b = prices_a + b_shift + noise

    # un cointegrated
    # returns_b = np.random.normal(0, 2, period)
    # prices_b = pd.Series(np.cumsum(returns_b), name='Prices A') + a_shift

    return prices_a, prices_b

def p_value(prices_a, prices_b):
    return coint(prices_a, prices_b)[1]

def z_score(spreads):
    return (spreads.iloc[-1] - spreads.mean())/spreads.std()

def log_returns(prices_a, prices_b):
    log_returns_a = (np.log(prices_a) - np.log(prices_a.shift(1)))[1:]
    log_returns_b = (np.log(prices_b) - np.log(prices_b.shift(1)))[1:]
    return log_returns_a, log_returns_b

def get_subset(ts_a, ts_b, end_index, sample_size):
    subset_a = ts_a[end_index-sample_size:end_index]
    subset_b = ts_b[end_index-sample_size:end_index]
    return subset_a, subset_b

# def build_trade(price_a, price_b):


if __name__ == '__main__':
    period = 1000
    prices_a, prices_b = generate_coint_series(period=period)
    z_upper = 1
    z_lower = -1
    p_threshold = 1
    non_coint_threshold = 50
    trade_values = []

    currently_trading = False
    rolling_balance = 0.00
    balances = [rolling_balance]
    current_trade = {}

    for i in range(period, len(prices_a)):
        subset_prices_a, subset_prices_b = get_subset(prices_a, prices_b, i, period)
        log_returns_a, log_returns_b = log_returns(subset_prices_a, subset_prices_b)
        hedge = get_hedge_ratio(log_returns_a, log_returns_b)
        spreads = get_spreads(subset_prices_a, subset_prices_b, hedge)
        zscore = z_score(spreads)
        p_val = p_value(subset_prices_a, subset_prices_b)

        if not currently_trading:
            if p_val <= p_threshold:
                if zscore > z_upper:
                    # the spread is more than the mean so we short A and long B
                    wallet_delta = hedge * subset_prices_a.iloc[-1] - subset_prices_b.iloc[-1]
                    current_trade = {
                        'open_price_a': subset_prices_a.iloc[-1],
                        'open_price_b': subset_prices_b.iloc[-1],
                        'hedge_ratio': hedge,
                        'longing': False,
                        'shorting': True,
                        'trade_value': wallet_delta,
                        'non_coint_count': 0
                    }
                    trade_values.append(wallet_delta)
                    rolling_balance += wallet_delta
                    currently_trading = True
                elif zscore < z_lower:
                    # the spread is less than the mean so we short B and long A
                    wallet_delta = subset_prices_b.iloc[-1] - hedge * subset_prices_a.iloc[-1]
                    current_trade = {
                        'open_price_a': subset_prices_a.iloc[-1],
                        'open_price_b': subset_prices_b.iloc[-1],
                        'hedge_ratio': hedge,
                        'longing': True,
                        'shorting': False,
                        'trade_value': wallet_delta,
                        'non_coint_count': 0
                    }
                    trade_values.append(wallet_delta)
                    rolling_balance += wallet_delta
                    currently_trading = True
        else:
            if p_val > p_threshold:
                if current_trade['non_coint_count'] > non_coint_threshold:
                    if current_trade['shorting']:
                        wallet_delta = subset_prices_b.iloc[-1] - current_trade['hedge_ratio'] * subset_prices_a.iloc[-1]
                        rolling_balance += wallet_delta
                        current_trade = {}
                        currently_trading = False
                    elif current_trade['longing']:
                        wallet_delta = current_trade['hedge_ratio'] * subset_prices_a.iloc[-1] - subset_prices_b.iloc[-1]
                        rolling_balance += wallet_delta
                        current_trade = {}
                        currently_trading = False
                    continue
                else:
                    current_trade['non_coint_count'] += 1

            if current_trade['shorting'] and zscore < z_lower:
                wallet_delta = subset_prices_b.iloc[-1] - subset_prices_a.iloc[-1] * current_trade['hedge_ratio']
                rolling_balance += wallet_delta
                current_trade = {}
                currently_trading = False
            elif current_trade['longing'] and zscore > z_upper:
                wallet_delta = current_trade['hedge_ratio'] * subset_prices_a.iloc[-1] - subset_prices_b.iloc[-1]
                rolling_balance += wallet_delta
                current_trade = {}
                currently_trading = False

        balances.append(rolling_balance)

    print 'the mean cost of trades is: ' + str(np.mean(trade_values))

    plt.plot(balances)
    plt.show()
