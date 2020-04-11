import numpy as np
import helpers.model_helper as helper
from services.cointegration_service import CointegrationService
import time

class Backtest:
    def __init__(self):
        self.setup_backtest()

    def setup_backtest(self):
        self.lookback_period = 80
        self.z_upper = 2
        self.z_lower = -2
        self.p_threshold = 0.05
        self.non_coint_threshold = 50

    def setup_pass(self):
        self.balance = 0.00
        self.balances = [self.balance]
        self.current_trade = {}

    def open_trade(self, p_val, zscore, price_a, price_b, hedge):
        if p_val <= self.p_threshold:
            if zscore > self.z_upper:
                # Go Short: the spread is more than the mean so we short B and long A
                self.current_trade = helper.build_trade(
                    price_a, price_b, hedge, 'short'
                )
                self.balance += helper.calculate_wallet_delta(
                    price_a, price_b, hedge, 'short'
                )
            elif zscore < self.z_lower:
                # Go Long: the spread is less than the mean so we short A and long B
                self.current_trade = helper.build_trade(
                    price_a, price_b, hedge, 'long'
                )
                self.balance += helper.calculate_wallet_delta(
                    price_a, price_b, hedge, 'long'
                )

    def close_trade(self, p_val, zscore, price_a, price_b, hedge):
        if p_val > self.p_threshold:
            if self.current_trade['non_coint_count'] > self.non_coint_threshold:
                self.close_for_non_cointegration(
                    p_val, zscore, price_a, price_b, hedge
                )
                self.current_trade = {}
                return
            else:
                self.current_trade['non_coint_count'] += 1

        if self.current_trade['type'] == 'short' and zscore < self.z_lower:
            self.balance += helper.calculate_wallet_delta(
                price_a, price_b, hedge, 'long'
            )
            self.current_trade = {}
        elif self.current_trade['type'] == 'long' and zscore > self.z_upper:
            self.balance += helper.calculate_wallet_delta(
                price_a, price_b, hedge, 'short'
            )
            self.current_trade = {}

    def close_for_non_cointegration(self, p_val, zscore, price_a, price_b, hedge):
        if self.current_trade['type'] == 'short':
            self.balance += helper.calculate_wallet_delta(
                price_a, price_b, hedge, 'long'
            )
        elif self.current_trade['type'] == 'long':
            self.balance += helper.calculate_wallet_delta(
                price_a, price_b, hedge, 'short'
            )

    def run(self, pairs):
        for pair, vals in pairs.items():
            prices_a = vals['prices_a']
            prices_b = vals['prices_b']

            self.setup_pass()

            for i in range(self.lookback_period, len(prices_a)):
                subset_prices_a, subset_prices_b = helper.get_subset(
                    prices_a, prices_b, i, self.lookback_period
                )
                subset_prices_a.name = 'subset_prices_a'
                subset_prices_b.name = 'subset_prices_b'

                zscore, hedge = helper.z_score(subset_prices_a, subset_prices_b)
                p_val = CointegrationService().p_value(
                    subset_prices_a, subset_prices_b
                )

                if not helper.open_to_trading(self.current_trade):
                    self.open_trade(
                        p_val,
                        zscore,
                        subset_prices_a.iloc[-1],
                        subset_prices_b.iloc[-1],
                        hedge
                    )
                else:
                    self.close_trade(
                        p_val,
                        zscore,
                        subset_prices_a.iloc[-1],
                        subset_prices_b.iloc[-1],
                        hedge
                    )

                self.balances.append(self.balance)
                print('balance (BTC): ', self.balance)

            # helper.save_plot(self.balance, self.balances, pair)
