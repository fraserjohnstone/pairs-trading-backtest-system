import numpy as np
import pandas as pd
import math
import statsmodels.api as sm
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import coint
import random
from historic_data import HistoricData

def get_hedge_ratio(log_returns_a, log_returns_b):
    log_returns_a = sm.add_constant(log_returns_a)
    results = sm.OLS(log_returns_b, log_returns_a).fit()
    log_returns_a = log_returns_a['log_returns_a']
    return results.params['log_returns_a']

def get_rolling_hedge_ratio(log_returns_a, log_returns_b):
    log_returns_a = sm.add_constant(log_returns_a)
    results = sm.OLS(log_returns_b, log_returns_a).fit()
    log_returns_a = log_returns_a['log_returns_a']
    return results.params['log_returns_a']

def get_spreads(prices_a, prices_b, hedge_ratio):
    spreads =  np.log(prices_b) - hedge_ratio * np.log(prices_a)
    return spreads

def generate_coint_series(sample_size=1000, a_shift=10, b_shift=5):
    noise = np.random.normal(0, 1, sample_size)

    prices_a = [a_shift]

    for i in range(1, sample_size):
        new_price = prices_a[i-1] + np.random.normal(0, 1, 1)[0]
        while new_price <= 10:
            new_price = prices_a[i-1] + np.random.normal(0, 1, 1)[0]
        prices_a.append(new_price)

    prices_a = pd.Series(prices_a)
    prices_b = prices_a + b_shift + noise

    # un cointegrated
    # returns_b = np.random.normal(0, 2, sample_size)
    # prices_b = pd.Series(np.cumsum(returns_b), name='Prices A') + a_shift

    return prices_a, prices_b

def p_value(prices_a, prices_b):
    return coint(prices_a, prices_b)[1]

def z_score(spreads):
    return (spreads.iloc[-1] - spreads.mean())/spreads.std()

def log_returns(prices_a, prices_b):
    log_returns_a = (np.log(prices_a) - np.log(prices_a.shift(1)))[1:]
    log_returns_b = (np.log(prices_b) - np.log(prices_b.shift(1)))[1:]
    log_returns_a.name = 'log_returns_a'
    log_returns_b.name = 'log_returns_b'
    return log_returns_a, log_returns_b

def get_subset(ts_a, ts_b, end_index, sample_size):
    subset_a = ts_a[end_index-sample_size:end_index]
    subset_b = ts_b[end_index-sample_size:end_index]
    return subset_a, subset_b

if __name__ == '__main__':
    sample_size = 1000
    lookback_period = 500
    # prices_a, prices_b = generate_coint_series(sample_size=sample_size)

    h_data = HistoricData(3.0, '3h', 2).gather()
    xmrbtc = h_data['XMRBTC']
    etcbtc = h_data['ETCBTC']

    prices_a = pd.Series([c[-2] for c in xmrbtc]).iloc[-1000:]
    prices_b = pd.Series([c[-2] for c in etcbtc]).iloc[-1000:]

    print len(prices_a)
    print len(prices_b)

    z_upper = 1
    z_lower = -1
    p_threshold = 0.05
    non_coint_threshold = 50
    trade_values = []

    currently_trading = False
    rolling_balance = 0.00
    balances = [rolling_balance]
    profits_as_percents = []

    current_trade = {}

    for i in range(lookback_period, len(prices_a)):
        subset_prices_a, subset_prices_b = get_subset(prices_a, prices_b, i, lookback_period)
        log_returns_a, log_returns_b = log_returns(subset_prices_a, subset_prices_b)
        hedge = get_hedge_ratio(log_returns_a, log_returns_b)
        spreads = get_spreads(subset_prices_a, subset_prices_b, hedge)
        zscore = z_score(spreads)
        p_val = p_value(subset_prices_a, subset_prices_b)

        if not currently_trading:
            if p_val <= p_threshold:
                if zscore > z_upper:
                    # the spread is less than the mean so we short B and long A
                    wallet_delta = subset_prices_b.iloc[-1] - hedge * subset_prices_a.iloc[-1]

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
                    # the spread is more than the mean so we short A and long B
                    wallet_delta = hedge * subset_prices_a.iloc[-1] - subset_prices_b.iloc[-1]

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
                    print 'closing for non cointegration'
                    print current_trade

                    profit = ((np.log(subset_prices_a.iloc[-1]) - np.log(current_trade['open_price_a'])) * current_trade['hedge_ratio']) + (np.log(subset_prices_b.iloc[-1]) - np.log(current_trade['open_price_b']))
                    print 'profit: ' + str(profit)
                    profits_as_percents.append(profit)

                    print

                    if current_trade['shorting']:
                        wallet_delta = current_trade['hedge_ratio'] * subset_prices_a.iloc[-1] - subset_prices_b.iloc[-1]
                        rolling_balance += wallet_delta
                        current_trade = {}
                        currently_trading = False
                    elif current_trade['longing']:
                        wallet_delta = subset_prices_b.iloc[-1] - current_trade['hedge_ratio'] * subset_prices_a.iloc[-1]
                        rolling_balance += wallet_delta
                        current_trade = {}
                        currently_trading = False

                    continue
                else:
                    current_trade['non_coint_count'] += 1

            if current_trade['shorting'] and zscore < z_lower:
                print 'closing for profit'
                print current_trade
                print 'current price a: ' + str(subset_prices_a.iloc[-1])
                print 'current price b: ' + str(subset_prices_b.iloc[-1])

                profit = ((np.log(subset_prices_a.iloc[-1]) - np.log(current_trade['open_price_a'])) * current_trade['hedge_ratio']) + (np.log(subset_prices_b.iloc[-1]) - np.log(current_trade['open_price_b']))
                print 'profit: ' + str(profit)
                profits_as_percents.append(profit)

                print

                wallet_delta = current_trade['hedge_ratio'] * subset_prices_a.iloc[-1] - subset_prices_b.iloc[-1]
                rolling_balance += wallet_delta
                current_trade = {}
                currently_trading = False
            elif current_trade['longing'] and zscore > z_upper:
                print 'closing for profit'
                print current_trade
                print 'current price a: ' + str(subset_prices_a.iloc[-1])
                print 'current price b: ' + str(subset_prices_b.iloc[-1])

                profit = ((np.log(subset_prices_a.iloc[-1]) - np.log(current_trade['open_price_a'])) * current_trade['hedge_ratio']) + (np.log(subset_prices_b.iloc[-1]) - np.log(current_trade['open_price_b']))
                print 'profit: ' + str(profit)
                profits_as_percents.append(profit)

                print

                wallet_delta = subset_prices_b.iloc[-1] - subset_prices_a.iloc[-1] * current_trade['hedge_ratio']
                rolling_balance += wallet_delta
                current_trade = {}
                currently_trading = False

        balances.append(rolling_balance)

    print 'the mean cost of trades is: ' + str(np.mean(trade_values))

    plt.plot(balances)
    plt.show()
