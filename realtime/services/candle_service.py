from binance.client import Client
import datetime

class CandleService:
    def __init__(self, interval='5m'):
        self.interval = interval
        self.client = Client(
            "WoZMHPqh51fvSsUE59jA64UosDRnYW2COriCPbz6nVWqPynzL4jf1oAa5ozMQbqT",
            "xaMl9wAiksc9E8LwtN8qbSBNCb2SIZK6zi9rBWg7lpoebZAzL9OhkKjhq96OYsco"
        )

    def candles(self, assets):
        candles = {}

        newest_point = datetime.datetime.now().strftime("%d %b %Y %H:%M:%S")
        oldest_point = (datetime.datetime.now()-datetime.timedelta(days=10)).strftime("%d %b %Y %H:%M:%S")

        for asset in assets:
            res = self.client.get_historical_klines(
                asset,
                self.interval,
                oldest_point,
                newest_point
            )
            candles[asset] = res
        return candles
