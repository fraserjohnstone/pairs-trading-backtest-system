from realtime.services.candle_service import CandleService
import pandas as pd

class PriceService:
    def __init__(self):
        self.candle_service = CandleService()

    def historic_prices(self, assets):
        candles = self.candle_service.candles(assets)
        prices = {}

        prices_a = [float(c[4]) for c in candles[assets[0]]]
        prices_b = [float(c[4]) for c in candles[assets[1]]]

        if len(prices_a) == len(prices_b):
            prices[assets[0] + '|' + assets[1]] = {
                assets[0]: pd.Series(prices_a),
                assets[1]: pd.Series(prices_b)
            }

        return prices
