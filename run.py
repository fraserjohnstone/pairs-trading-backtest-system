import numpy as np
import pandas as pd
import math
import statsmodels.api as sm
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import coint
import random

def get_hedge_ratio(prices_a, prices_b):
    # log_returns_a = (np.log(prices_a) - np.log(prices_a.shift(1)))[1:]
    # log_returns_b = (np.log(prices_b) - np.log(prices_b.shift(1)))[1:]
    #
    # log_returns_a.name = 'Log returns A'
    # log_returns_b.name = 'Log returns B'
    # log_returns_a = sm.add_constant(log_returns_a)
    #
    # results = sm.OLS(log_returns_b, log_returns_a).fit()
    # return results.params['Log returns A']

    prices_a = sm.add_constant(prices_a)
    results = sm.OLS(prices_b, prices_a).fit()
    prices_a = prices_a['sample prices A']
    return results.params[1]

def get_spreads(prices_a, prices_b, hedge_ratio):
    spreads = prices_b - (hedge_ratio * prices_a)
    spreads.name = 'Spreads'

    return spreads

def generate_coint_series(num_samples=100, a_shift=50, b_shift=0):
    noise = np.random.normal(0, 1, num_samples)

    returns_a = np.random.normal(0, 1, num_samples)
    prices_a = pd.Series(np.cumsum(returns_a), name='Prices A') + a_shift
    prices_b = prices_a + b_shift + noise
    prices_b.name = 'Prices B'

    return prices_a, prices_b

def p_value(prices_a, prices_b):
    return coint(prices_a, prices_b)[1]

def z_score(spreads):
    return spreads.iloc[-1] - (spreads.mean()/spreads.std())

def calculate_profit(current_trade, current_prices_a, current_prices_b):
    return math.log(current_prices_a[-1])-math.log(current_trade['open_price_a'])+hedge_ratio*(math.log(current_prices_b[-1])-math.log(current_trade['open_price_b']))

if __name__ == '__main__':
    num_samples = 10000000
    lookback_period = 1000
    entry_threshold = 1
    exit_threshold = -1

    prices_a, prices_b = generate_coint_series(num_samples=num_samples)

    currently_trading = False
    rolling_balance = 10000.00
    current_trade = {}
    transaction_type = ''

    for i in range(lookback_period, num_samples):

        sample_prices_a = prices_a[i-lookback_period:i]
        sample_prices_a.name = 'sample prices A'

        sample_prices_b = prices_b[i-lookback_period:i]
        sample_prices_b.name = 'sample prices B'

        current_hedge_ratio = get_hedge_ratio(sample_prices_a, sample_prices_b)
        spreads = get_spreads(sample_prices_a, sample_prices_b, current_hedge_ratio)
        zscore = z_score(spreads)

        if not currently_trading:
            if zscore < -1.3:
                pass
                # wallet_delta = sample_prices_a.iloc[-1] - sample_prices_b.iloc[-1]
                # wallet_delta = sample_prices_a.iloc[-1] - (sample_prices_b.iloc[-1] * current_hedge_ratio)
                # current_trade = {
                #     'open_price_a': sample_prices_a.iloc[-1],
                #     'open_price_b': sample_prices_b.iloc[-1],
                #     'hedge_ratio': current_hedge_ratio,
                #     'longing': True,
                #     'shorting': False
                #     'trade_value': wallet_delta
                # }
                # rolling_balance += wallet_delta
                # currently_trading = True
            elif zscore > 1.3:
                # the spread is more than the mean so we short B and long A
                wallet_delta = sample_prices_b.iloc[-1] - sample_prices_a.iloc[-1]
                # wallet_delta = (sample_prices_b.iloc[-1] * current_hedge_ratio) - sample_prices_a.iloc[-1]s_b.iloc[-1] * current_hedge_ratio
                current_trade = {
                    'open_price_a': sample_prices_a.iloc[-1],
                    'open_price_b': sample_prices_b.iloc[-1],
                    'hedge_ratio': current_hedge_ratio,
                    'longing': False,
                    'shorting': True,
                    'trade_value': wallet_delta
                }
                rolling_balance += wallet_delta
                currently_trading = True
        else:
            if current_trade['longing'] and zscore > 1.3:
                pass
                # wallet_delta = (sample_prices_b.iloc[-1] * current_trade['hedge_ratio'])-sample_prices_a.iloc[-1]
                # if wallet_delta < 0:
                #     transaction_type = 'loss'
                # else:
                #     transaction_type = 'profit'
                # rolling_balance += wallet_delta
                # current_trade = {}
                # currently_trading = False
                # print str(i) + '. transactiontype is a ' + transaction_type + ' - rolling balance: ' + str(rolling_balance)
            elif current_trade['shorting'] and zscore < -1.3:
                wallet_delta = sample_prices_a.iloc[-1]-sample_prices_b.iloc[-1]
                # wallet_delta = sample_prices_a.iloc[-1]-(sample_prices_b.iloc[-1] * current_trade['hedge_ratio'])
                if wallet_delta < 0.0:
                    transaction_type = 'loss'
                else:
                    transaction_type = 'profit'
                rolling_balance += wallet_delta
                print
                print 'trade value when placed was: ' + str(current_trade['trade_value'])
                print 'wallet delta is:' + str(wallet_delta)
                print str(i) + '. transaction type is a ' + transaction_type + ' - rolling balance: ' + str(rolling_balance)
                current_trade = {}
                currently_trading = False
