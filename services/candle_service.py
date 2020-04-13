from binance.client import Client
import datetime
from services.asset_service import AssetService
import time

class CandleService:
    def __init__(self):
        self.asset_service = AssetService()

    def candles(self, days_to_gather, interval, assets=None):
        if not assets:
            assets = self.asset_service.all()
        candles = {}

        newest_point = datetime.datetime.now().strftime("%d %b %Y %H:%M:%S")
        oldest_point = (datetime.datetime.now()-datetime.timedelta(days=days_to_gather)).strftime("%d %b %Y %H:%M:%S")

        i = 1

        for asset in assets:
            print('gathering asset', asset, ' --- ', i, 'of', len(assets))
            res = self.client().get_historical_klines(
                asset,
                interval,
                oldest_point,
                newest_point
            )
            candles[asset] = res
            i += 1

        return candles

    def client(self):
        return Client(
            "WoZMHPqh51fvSsUE59jA64UosDRnYW2COriCPbz6nVWqPynzL4jf1oAa5ozMQbqT",
            "xaMl9wAiksc9E8LwtN8qbSBNCb2SIZK6zi9rBWg7lpoebZAzL9OhkKjhq96OYsco"
        )
