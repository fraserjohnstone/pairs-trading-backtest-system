from binance.client import Client
from datetime import datetime, timedelta
import requests

class TickerService:
    def __init__(self):
        self.client = Client(
            "WoZMHPqh51fvSsUE59jA64UosDRnYW2COriCPbz6nVWqPynzL4jf1oAa5ozMQbqT",
            "xaMl9wAiksc9E8LwtN8qbSBNCb2SIZK6zi9rBWg7lpoebZAzL9OhkKjhq96OYsco"
        )

    def ticker_for(self, asset):
        res = self.client.get_orderbook_tickers()
        ticker = {}

        for symbol_info in res:
            if symbol_info['symbol'] == asset:
                ticker['ask'] = float(symbol_info['askPrice'])
                ticker['bid'] = float(symbol_info['bidPrice'])
                ticker['avg_price'] = (float(symbol_info['askPrice'])+float(symbol_info['bidPrice']))/2.0
        return ticker
