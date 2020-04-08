import numpy as np
import backtest.helpers.model_helper as helper
from realtime.services.cointegration_service import CointegrationService
from realtime.services.ticker_service import TickerService
from realtime.services.price_service import PriceService
import time
import pandas as pd
import matplotlib.pyplot as plt

class Model:
    def __init__(self):
        self.setup_backtest()

    def setup_backtest(self):
        self.lookback_period = 80
        self.z_upper = 1
        self.z_lower = 1
        self.p_threshold = 0.05
        self.non_coint_threshold = 50
        self.ticker_service = TickerService()
        self.price_service = PriceService()

    def setup_pass(self):
        self.balance = 0.00
        self.balances = [self.balance]
        self.current_trade = {}
        self.pass_number = 1

    def open_trade(self, p_val, zscore, ticker_data_a, ticker_data_b, hedge):
        if p_val <= self.p_threshold:
            if zscore > self.z_upper:
                print('opening trade')
                # Go Short: the spread is more than the mean so we short B and long A
                price_a = ticker_data_a['ask']
                price_b = ticker_data_b['bid']

                self.current_trade = helper.build_trade(
                    price_a, price_b, hedge, 'short'
                )
                self.balance += helper.calculate_wallet_delta(
                    price_a, price_b, hedge, 'short'
                )
            elif zscore < self.z_lower:
                print('opening trade')
                # Go Long: the spread is less than the mean so we short A and long B
                price_a = ticker_data_a['bid']
                price_b = ticker_data_b['ask']

                self.current_trade = helper.build_trade(
                    price_a, price_b, hedge, 'long'
                )
                self.balance += helper.calculate_wallet_delta(
                    price_a, price_b, hedge, 'long'
                )

    def close_trade(self, p_val, zscore, ticker_data_a, ticker_data_b, hedge):
        if p_val > self.p_threshold:
            print('closing trade')
            if self.current_trade['non_coint_count'] > self.non_coint_threshold:
                self.close_for_non_cointegration(
                    p_val, zscore, ticker_data_a, ticker_data_b, hedge
                )
                return
            else:
                self.current_trade['non_coint_count'] += 1

        if self.current_trade['type'] == 'short' and zscore < self.z_lower:
            print('closing trade')
            price_a = ticker_data_a['bid']
            price_b = ticker_data_b['ask']

            self.balance += helper.calculate_wallet_delta(
                price_a, price_b, hedge, 'long'
            )
            self.current_trade = {}
        elif self.current_trade['type'] == 'long' and zscore > self.z_upper:
            print('closing trade')
            price_a = ticker_data_a['ask']
            price_b = ticker_data_b['bid']

            self.balance += helper.calculate_wallet_delta(
                price_a, price_b, hedge, 'short'
            )
            self.current_trade = {}

    def close_for_non_cointegration(self, p_val, zscore, ticker_data_a, ticker_data_b, hedge):
        if self.current_trade['type'] == 'short':
            print('closing trade')
            price_a = ticker_data_a['bid']
            price_b = ticker_data_b['ask']

            self.balance += helper.calculate_wallet_delta(
                price_a, price_b, hedge, 'long'
            )
            self.current_trade = {}
        elif self.current_trade['type'] == 'long':
            print('closing trade')
            price_a = ticker_data_a['ask']
            price_b = ticker_data_b['bid']

            self.balance += helper.calculate_wallet_delta(
                price_a, price_b, hedge, 'short'
            )
            self.current_trade = {}

    def run(self, asset_a, asset_b):
        self.setup_pass()

        while True:
            historic_prices = self.price_service.historic_prices([asset_a, asset_b])
            historic_prices_a = historic_prices[asset_a+'|'+asset_b][asset_a]
            historic_prices_b = historic_prices[asset_a+'|'+asset_b][asset_b]

            ticker_data_a = self.ticker_service.ticker_for(asset_a)
            ticker_data_b = self.ticker_service.ticker_for(asset_b)

            historic_prices_a = pd.Series(np.append(historic_prices_a.values, ticker_data_a['avg_price']))
            historic_prices_b = pd.Series(np.append(historic_prices_b.values, ticker_data_b['avg_price']))
            historic_prices_a.name = 'subset_prices_a'
            historic_prices_b.name = 'subset_prices_b'

            plt.plot(historic_prices_a)
            plt.plot(historic_prices_b)
            plt.show()

            zscore, hedge = helper.z_score(historic_prices_a, historic_prices_b)
            p_val = CointegrationService().p_value(
                historic_prices_a, historic_prices_b
            )

            print('pass ' + str(self.pass_number) + ' - balance (BTC): ', self.balance)
            print('z_score: ', zscore)
            print('hedge: ', hedge)
            print('p value: ', p_val)
            print()

            if not helper.open_to_trading(self.current_trade):
                self.open_trade(
                    p_val,
                    zscore,
                    ticker_data_a,
                    ticker_data_b,
                    hedge
                )
            else:
                self.close_trade(
                    p_val,
                    zscore,
                    ticker_data_a,
                    ticker_data_b,
                    hedge
                )

            self.balances.append(self.balance)
            self.pass_number += 1

            time.sleep(60*5)
