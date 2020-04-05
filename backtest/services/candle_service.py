from datetime import datetime, timedelta
import requests
from backtest.services.asset_service import AssetService

class CandleService:
    def __init__(self, num_candles=10000, time_frame='15m'):
        self.num_candles = num_candles
        self.time_frame = time_frame
        self.asset_service = AssetService()

    def candles(self):
        candles = {}
        for asset in self.asset_service.all():
            res = self.response(asset)

            if "error" in res:
                print(str(res))
            else:
                candles[asset] = res
        return candles

    def params(self):
        now = datetime.now()
        one_month_ago = now - timedelta(days=30)
        return {
            'limit': self.num_candles,
            'end': str(int(one_month_ago.timestamp() * 1000))
        }

    def request_url(self, asset):
        return 'https://api-pub.bitfinex.com/v2/candles/trade:' + self.time_frame + ':t' + asset + '/hist'

    def response(self, asset):
        r = requests.get(self.request_url(asset), params=self.params())
        res = r.json()
        return res
