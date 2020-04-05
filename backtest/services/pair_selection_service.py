from backtest.services.cointegration_service import CointegrationService
from backtest.services.price_service import PriceService

class PairSelectionService:
    def __init__(self):
        self.cointegration_service = CointegrationService()
        self.price_service = PriceService()

    def selected_pairs(self):
        selected = {}
        for pair, prices in self.price_service.prices().items():
            asset_a, asset_b = pair.split('|')
            prices_a = prices[asset_a]
            prices_b = prices[asset_b]

            print('analysing', pair)

            if self.displays_cointegration(prices_a, prices_b):
                selected[pair] = {
                    'prices_a': prices_a,
                    'prices_b': prices_b
                }

        return selected

    def displays_cointegration(self, prices_a, prices_b):
        criteria_met = False

        for interval in [1, 2, 6, 12, 24]:
            if self.cointegrated_at_interval(prices_a, prices_b, interval):
                criteria_met = True
                break

        for period in [80, 160, 320, 640]:
            if self.cointegrated_over_period(prices_a, prices_b, period):
                criteria_met = True
                break

        print('criteria met?: ', criteria_met)
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
