import numpy as np
import pandas as pd
import math
import statsmodels.api as sm
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import coint
import random
from data_extractor import get_pep_ccl

def get_hedge_ratio(log_returns_a, log_returns_b):
    log_returns_a = sm.add_constant(log_returns_a)
    results = sm.OLS(log_returns_b, log_returns_a).fit()
    log_returns_a = log_returns_a['Log returns A']
    return results.params['Log returns A']

def get_spreads(prices_a, prices_b, hedge_ratio):
    spreads = hedge_ratio * np.log(prices_a) - np.log(prices_b)
    spreads.name = 'Spreads'

    return spreads

def generate_coint_series(num_samples=100, a_shift=10, b_shift=5):
    noise = np.random.normal(0, 1, num_samples)

    prices_a = [a_shift]

    for i in range(1, num_samples):
        new_price = prices_a[i-1] + np.random.normal(0, 1, 1)[0]
        while new_price <= 10:
            new_price = prices_a[i-1] + np.random.normal(0, 1, 1)[0]
        prices_a.append(new_price)

    prices_a = pd.Series(prices_a, name='Prices A')
    prices_b = prices_a + b_shift + noise
    prices_b.name = 'Prices B'

    # un cointegrated
    # returns_b = np.random.normal(0, 2, num_samples)
    # prices_b = pd.Series(np.cumsum(returns_a), name='Prices A') + a_shift

    return prices_a, prices_b

def p_value(prices_a, prices_b):
    return coint(prices_a, prices_b)[1]

def z_score(spreads):
    return (spreads.iloc[-1] - spreads.mean())/spreads.std()

if __name__ == '__main__':
    num_samples = 1000000
    lookback_period = 100
    z_upper = 1
    z_lower = -1
    p_threshold = 1
    non_coint_threshold = 50
    trade_values = []

    # prices_a, prices_b = get_pep_ccl()

    prices_a, prices_b = generate_coint_series(num_samples=num_samples)

    currently_trading = False
    rolling_balance = 10000.00
    balances = [rolling_balance]
    current_trade = {}
    transaction_type = ''

    for i in range(lookback_period, num_samples):
        sample_prices_a = prices_a[i-lookback_period:i]
        sample_prices_a.name = 'sample prices A'

        sample_prices_b = prices_b[i-lookback_period:i]
        sample_prices_b.name = 'sample prices B'

        log_returns_a = (np.log(sample_prices_a) - np.log(sample_prices_a.shift(1)))[1:]
        log_returns_b = (np.log(sample_prices_b) - np.log(sample_prices_b.shift(1)))[1:]

        log_returns_a.name = 'Log returns A'
        log_returns_b.name = 'Log returns B'

        hedge = get_hedge_ratio(log_returns_a, log_returns_b)
        # print 'hedge is: ' + str(hedge)

        spreads = get_spreads(sample_prices_a, sample_prices_b, hedge)
        zscore = z_score(spreads)
        p_val = p_value(sample_prices_a, sample_prices_b)

        if not currently_trading:
            if p_val <= p_threshold:
                if zscore > z_upper:
                    # the spread is more than the mean so we short A and long B
                    wallet_delta = hedge * sample_prices_a.iloc[-1] - sample_prices_b.iloc[-1]
                    current_trade = {
                        'open_price_a': sample_prices_a.iloc[-1],
                        'open_price_b': sample_prices_b.iloc[-1],
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
                    wallet_delta = sample_prices_b.iloc[-1] - hedge * sample_prices_a.iloc[-1]
                    current_trade = {
                        'open_price_a': sample_prices_a.iloc[-1],
                        'open_price_b': sample_prices_b.iloc[-1],
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
                    print
                    print 'closing for long running non cointegration'
                    if current_trade['shorting']:
                        wallet_delta = sample_prices_b.iloc[-1] - current_trade['hedge_ratio'] * sample_prices_a.iloc[-1]
                        rolling_balance += wallet_delta
                        print str(i) + '. rolling balance: ' + str(rolling_balance)
                        current_trade = {}
                        currently_trading = False
                    elif current_trade['longing']:
                        wallet_delta = current_trade['hedge_ratio'] * sample_prices_a.iloc[-1] - sample_prices_b.iloc[-1]
                        rolling_balance += wallet_delta
                        print str(i) + '. rolling balance: ' + str(rolling_balance)
                        current_trade = {}
                        currently_trading = False
                    continue
                else:
                    current_trade['non_coint_count'] += 1

            if current_trade['shorting'] and zscore < z_lower:
                wallet_delta = sample_prices_b.iloc[-1] - sample_prices_a.iloc[-1] * current_trade['hedge_ratio']
                rolling_balance += wallet_delta
                print str(i) + '. rolling balance: ' + str(rolling_balance)
                current_trade = {}
                currently_trading = False
            elif current_trade['longing'] and zscore > z_upper:
                wallet_delta = current_trade['hedge_ratio'] * sample_prices_a.iloc[-1] - sample_prices_b.iloc[-1]
                rolling_balance += wallet_delta
                print str(i) + '. rolling balance: ' + str(rolling_balance)
                current_trade = {}
                currently_trading = False

        balances.append(rolling_balance)

    print 'the mean cost of trades is: ' + str(np.mean(trade_values))

    plt.plot(balances)
    plt.show()
