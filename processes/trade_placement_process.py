from models.realtime import Realtime

class TradePlacementProcess:
    def run(self):
        Realtime().run('LTCBTC', 'ETHBTC')
