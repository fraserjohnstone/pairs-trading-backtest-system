import numpy as np
import backtest.helpers.model_helper as helper
from backtest.services.cointegration_service import CointegrationService
import matplotlib.pyplot as plt

def config():
    return {
        'lookback_period': 80,
        'z_upper': 1,
        'z_lower': -1,
        'p_threshold': 0.05,
        'non_coint_threshold': 50,
        'trade_values': []
    }

def run_test(pairs):
    for pair, vals in pairs.items():
        prices_a = vals['prices_a']
        prices_b = vals['prices_b']

        currently_trading = False
        rolling_balance = 0.00
        balances = [rolling_balance]
        profits_as_percents = []

        current_trade = {}

        for i in range(config()['lookback_period'], len(prices_a)):
            subset_prices_a, subset_prices_b = helper.get_subset(
                prices_a,
                prices_b, i,
                config()['lookback_period']
            )
            subset_prices_a.name = 'subset_prices_a'
            subset_prices_b.name = 'subset_prices_b'

            zscore, hedge = helper.z_score(subset_prices_a, subset_prices_b)
            p_val = CointegrationService().p_value(
                subset_prices_a,
                subset_prices_b
            )

            print()
            print('zscore: ', zscore)
            print('p_value: ', p_val)
            print('balance: ', rolling_balance)
            print('hedge ratio: ', hedge)
            print('average percentage profit: ', "%.2f" % (np.mean(profits_as_percents)*100))

            if not currently_trading:
                if p_val <= config()['p_threshold']:
                    if zscore > config()['z_upper']:
                        # the spread is more than the mean so we short B and long A
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
                        config()['trade_values'].append(wallet_delta)
                        rolling_balance += wallet_delta
                        currently_trading = True
                    elif zscore < config()['z_lower']:
                        # the spread is less than the mean so we short A and long B
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
                        config()['trade_values'].append(wallet_delta)
                        rolling_balance += wallet_delta
                        currently_trading = True
            else:
                if p_val > config()['p_threshold']:
                    if current_trade['non_coint_count'] > config()['non_coint_threshold']:
                        profit = ((np.log(subset_prices_a.iloc[-1]) - np.log(current_trade['open_price_a'])) * current_trade['hedge_ratio']) + (np.log(subset_prices_b.iloc[-1]) - np.log(current_trade['open_price_b']))
                        profits_as_percents.append(profit)

                        if current_trade['shorting']:
                            wallet_delta = current_trade['hedge_ratio'] * subset_prices_a.iloc[-1] - subset_prices_b.iloc[-1]
                            rolling_balance += wallet_delta
                            current_trade = {}
                            currently_trading = False
                            print('rolling balance is :', rolling_balance)
                        elif current_trade['longing']:
                            wallet_delta = subset_prices_b.iloc[-1] - current_trade['hedge_ratio'] * subset_prices_a.iloc[-1]
                            rolling_balance += wallet_delta
                            current_trade = {}
                            currently_trading = False

                            print('rolling balance is :', rolling_balance)
                        continue
                    else:
                        current_trade['non_coint_count'] += 1

                if current_trade['shorting'] and zscore < config()['z_lower']:
                    profit = ((np.log(subset_prices_a.iloc[-1]) - np.log(current_trade['open_price_a'])) * current_trade['hedge_ratio']) + (np.log(subset_prices_b.iloc[-1]) - np.log(current_trade['open_price_b']))
                    profits_as_percents.append(profit)

                    wallet_delta = current_trade['hedge_ratio'] * subset_prices_a.iloc[-1] - subset_prices_b.iloc[-1]
                    rolling_balance += wallet_delta
                    current_trade = {}
                    currently_trading = False
                elif current_trade['longing'] and zscore > config()['z_upper']:
                    profit = ((np.log(subset_prices_a.iloc[-1]) - np.log(current_trade['open_price_a'])) * current_trade['hedge_ratio']) + (np.log(subset_prices_b.iloc[-1]) - np.log(current_trade['open_price_b']))
                    profits_as_percents.append(profit)

                    wallet_delta = subset_prices_b.iloc[-1] - subset_prices_a.iloc[-1] * current_trade['hedge_ratio']
                    rolling_balance += wallet_delta
                    current_trade = {}
                    currently_trading = False

            balances.append(rolling_balance)

        if rolling_balance > 0:
            plt.plot(balances)
            plt.title('Rolling Balance ('+pair+')')
            plt.xlabel('Passes')
            plt.ylabel('Balance')

            plt.draw()
            plt.savefig(pair+'.png')
            plt.clf()
