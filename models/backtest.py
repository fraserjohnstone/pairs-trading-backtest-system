import numpy as np
import helpers.model_helper as helper
from services.cointegration_service import CointegrationService
import time
from wallet import Wallet
import json

class Backtest:
    def __init__(self):
        self.setup_backtest()

    def setup_backtest(self):
        self.lookback_period = 80
        self.z_in_upper = 2
        self.z_in_lower = -2
        self.z_out_upper = 0
        self.z_out_lower = 0
        self.p_threshold = 0.05
        self.non_coint_threshold = 50

    def setup_pass(self):
        self.wallet = Wallet()
        self.current_trade = {}
        self.profits = []
        self.num_trades = 0
        self.rolling_holdings = []

    def open_trade(self, p_val, zscore, price_a, price_b, hedge):
        if p_val <= self.p_threshold:
            if zscore > self.z_in_upper:
                # Go Short: the spread is more than the mean so we short B and long A
                self.current_trade = helper.build_trade(
                    price_a, price_b, hedge, 'short'
                )
                self.wallet.sell('b', self.current_trade['quantity_b'], price_b)
                self.wallet.buy('a', self.current_trade['quantity_a'], price_a)
                self.num_trades += 1
                return

            if zscore < self.z_in_lower:
                # Go Long: the spread is less than the mean so we short A and long B
                self.current_trade = helper.build_trade(
                    price_a, price_b, hedge, 'long'
                )
                self.wallet.sell('a', self.current_trade['quantity_a'], price_a)
                self.wallet.buy('b', self.current_trade['quantity_b'], price_b)
                self.num_trades += 1
                return

    def close_trade(self, p_val, zscore, price_a, price_b, hedge):
        # if p_val > self.p_threshold:
        #     if self.current_trade['non_coint_count'] > self.non_coint_threshold:
        #         self.close_for_non_cointegration(
        #             p_val, zscore, price_a, price_b, hedge
        #         )
        #         self.current_trade = {}
        #         return
        #     else:
        #         self.current_trade['non_coint_count'] += 1
        if self.current_trade['type'] == 'short' and zscore < self.z_out_lower:
            self.wallet.sell('a', self.current_trade['quantity_a'], price_a)
            self.wallet.buy('b', self.current_trade['quantity_b'], price_b)
            self.current_trade = {}
            return

        if self.current_trade['type'] == 'long' and zscore > self.z_out_upper:
            self.wallet.sell('b', self.current_trade['quantity_b'], price_b)
            self.wallet.buy('a', self.current_trade['quantity_a'], price_a)
            self.current_trade = {}
            return

    # def close_for_non_cointegration(self, p_val, zscore, price_a, price_b, hedge):
    #     if self.current_trade['type'] == 'short':
    #         self.wallet.sell('a', self.current_trade['quantity_a'], price_a)
    #         self.wallet.buy('b', self.current_trade['quantity_b'], price_b)
    #     elif self.current_trade['type'] == 'long':
    #         self.wallet.sell('b', self.current_trade['quantity_b'], price_b)
    #         self.wallet.buy('a', self.current_trade['quantity_a'], price_a)

    def run(self, pairs):
        for pair, vals in pairs.items():
            # prices_a, prices_b = helper.generate_coint_series()
            prices_a = vals['prices_a']
            prices_b = vals['prices_b']

            self.setup_pass()

            for i in range(self.lookback_period, len(prices_a)):
                subset_prices_a, subset_prices_b = helper.get_subset(
                    prices_a, prices_b, i, self.lookback_period
                )
                subset_prices_a.name = 'subset_prices_a'
                subset_prices_b.name = 'subset_prices_b'

                hedge = helper.simple_hedge(subset_prices_a, subset_prices_b)
                spreads = helper.simple_spreads(subset_prices_a, subset_prices_b, 0)
                zscore = helper.simple_zscore(spreads)

                p_val = CointegrationService().p_value(
                    subset_prices_a, subset_prices_b
                )

                if helper.currently_trading(self.current_trade):
                    self.close_trade(
                        p_val,
                        zscore,
                        subset_prices_a.iloc[-1],
                        subset_prices_b.iloc[-1],
                        hedge
                    )
                else:
                    self.open_trade(
                        p_val,
                        zscore,
                        subset_prices_a.iloc[-1],
                        subset_prices_b.iloc[-1],
                        hedge
                    )

                self.rolling_holdings.append(self.wallet.holdings['btc'])

                print('holdings (BTC): ', self.wallet.holdings['btc'])
                print('holdings (Asset A): ', self.wallet.holdings['a'])
                print('holdings (Asset B): ', self.wallet.holdings['b'])
                print('zscore:', zscore)
                print('hedge:', hedge)
                print('-'*20)
                print()

            result = {
                'pair': pair,
                'holdings': self.wallet.holdings['btc'],
                'rolling_holdings': self.rolling_holdings,
                'avg_ratio': vals['avg_ratio'],
                'num_trades': self.num_trades
            }
            with open('backtest_results.json', 'r') as f:
                results_list = json.load(f)
                results_list.append(result)
            with open('backtest_results.json', 'w') as f:
                json.dump(results_list, f)
