from services.candle_service import CandleService
import pandas as pd

class PriceService:
    def __init__(self):
        self.candle_service = CandleService()

    def historic_prices(self, days_to_gather, interval, assets):
        candles = self.candle_service.candles(days_to_gather, interval, assets)
        prices = {}

        for asset in assets:
            prices[asset] = pd.Series([float(c[4]) for c in candles[asset]])
        return prices
