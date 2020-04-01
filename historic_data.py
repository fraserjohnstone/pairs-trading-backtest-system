import time
import sys
import requests
import config

class HistoricData:
    def __init__(self, step_hours, time_frame, years_to_gather):
        self.one_year_ms = 1539945317425
        self.years_to_gather = years_to_gather
        self.max_candle_limit = 4999

        self.step_hours = step_hours
        self.time_frame = time_frame
        self.days_to_gather = self.years_to_gather * 356
        self.step_ms = 1000.0 * 60 * 60 * step_hours
        self.end_ts = int(round(time.time() * 1000))
        self.start_ts = self.end_ts - (self.one_year_ms * self.years_to_gather)
        self.total_candle_count = (24.0/step_hours) * self.days_to_gather
        print 'total expected candle count', self.total_candle_count
        self.candles_per_pass = []
        self.get_num_candles_per_pass()

    def get_num_candles_per_pass(self):
        while self.total_candle_count > 0:
            if self.total_candle_count >= self.max_candle_limit:
                self.candles_per_pass.append(self.max_candle_limit)
                self.total_candle_count -= self.max_candle_limit
            else:
                self.candles_per_pass.append(self.total_candle_count)
                self.total_candle_count = 0

    def get_candles_for_asset(self, asset_pair, time_frame, limit, start):
        url = 'https://api-pub.bitfinex.com/v2/candles/trade:' + time_frame + ':t' + asset_pair + '/hist'
        params = { 'limit': limit, 'start': start }
        r = requests.get(url, params = params)
        return r.json()

    def get_all_asset_candles(self, candles, num_candles):
        for asset in config.assets()+['BTCGBP']:
            res = self.get_candles_for_asset(
                asset, self.time_frame, int(num_candles), self.start_ts
            )

            if "error" in res:
                print str(res)
                return False
            else:
                candles[asset] = res
        return True

    def gather(self):
        print 'getting for time frame', self.time_frame

        all_candles = {}
        pass_number = 1

        for num_candles in self.candles_per_pass:
            while True:
                print 'starting pass', pass_number, 'of', len(self.candles_per_pass), '(', round((float(pass_number)/float(len(self.candles_per_pass)))*100.0), '%)'
                print 'collecting', num_candles, 'on pass', pass_number

                candles = {}

                try:
                    if self.get_all_asset_candles(candles, num_candles):
                        for asset, asset_candles in candles.items():
                            if asset in all_candles.keys():
                                all_candles[asset] += asset_candles
                            else:
                                all_candles[asset] = asset_candles

                        pass_number += 1
                        self.start_ts += self.step_ms
                        break
                    else:
                        print 'error rate triggered - sleeping'
                        time.sleep(120)
                        continue
                except:
                    print 'caught error - sleeping'
                    time.sleep(120)
                    continue

        return all_candles


# for testing
if __name__ == '__main__':
    HistoricData(float(sys.argv[1]), sys.argv[2]).gather()
