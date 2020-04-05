from backtest.services.candle_service import CandleService
from backtest.services.asset_service import AssetService
import pandas as pd

class PriceService:
    def __init__(self):
        self.candle_service = CandleService()
        self.asset_service = AssetService()

    def prices(self):
        candles = self.candle_service.candles()
        prices = {}

        for pair in self.asset_service.possible_pairs():
            asset_a, asset_b = pair
            prices_a = [c[2] for c in candles[asset_a]]
            prices_b = [c[2] for c in candles[asset_b]]

            if len(prices_a) == len(prices_b):
                prices[asset_a + '|' + asset_b] = {
                    asset_a: pd.Series(prices_a),
                    asset_b: pd.Series(prices_b)
                }

        return prices
