from services.cointegration_service import CointegrationService
from services.price_service import PriceService
from services.asset_service import AssetService

class PairSelectionService:
    def __init__(self):
        self.cointegration_service = CointegrationService()
        self.price_service = PriceService()
        self.asset_service = AssetService()
        self.periods = [80, 160, 320]
        self.intervals = [1, 2, 4, 8]

    def from_pickled_candles(self, candles):
        possible_pairs = self.asset_service.possible_pairs()
        assets = self.asset_service.all()
        asset_prices = self.price_service.historic_prices_from_pickled_candles(assets, candles)

        return self.selected(asset_prices, possible_pairs)


    def from_live_candles(self, days_to_gather, interval, assets=None, possible_pairs=None):
        if not assets:
            assets = self.asset_service.all()
        if not possible_pairs:
            possible_pairs = self.asset_service.possible_pairs()
        asset_prices = self.price_service.historic_prices(days_to_gather, interval, assets)

        return self.selected(asset_prices, possible_pairs)

    def selected(self, asset_prices, possible_pairs):
        selected_pairs = {}

        for paired_assets in possible_pairs:
            print('analysing', paired_assets)
            asset_a, asset_b = paired_assets
            prices_a = asset_prices[asset_a]
            prices_b = asset_prices[asset_b]

            try:
                ratio = (prices_a/prices_b).mean()
            except:
                continue

            try:
                if self.displays_cointegration(prices_a[-320:], prices_b[-320:]) and 0.85 <= ratio <= 1.15:
                    print('  - pair', paired_assets, 'shows cointegration with ratio of: ', ratio)
                    selected_pairs[asset_a+'|'+asset_b] = {
                        'prices_a': prices_a,
                        'prices_b': prices_b,
                        'avg_ratio': ratio
                    }
            except:
                continue
        return selected_pairs

    def displays_cointegration(self, prices_a, prices_b):
        criteria_met = False

        for interval in self.intervals:
            if self.cointegrated_at_interval(prices_a, prices_b, interval):
                criteria_met = True
                break

        if not criteria_met:
            for period in self.periods:
                if self.cointegrated_over_period(prices_a, prices_b, period):
                    criteria_met = True
                    break

        return criteria_met

    def cointegrated_at_interval(self, prices_a, prices_b, interval):
        return self.cointegration_service.sufficiently_cointegrated(
            prices_a[::interval],
            prices_b[::interval]
        )

    def cointegrated_over_period(self, prices_a, prices_b, period):
        return self.cointegration_service.sufficiently_cointegrated(
            prices_a[-period:],
            prices_b[-period:]
        )
