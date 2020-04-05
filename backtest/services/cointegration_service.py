from statsmodels.tsa.stattools import coint

class CointegrationService:
    def __init__(self, p_threshold=0.05):
        self.p_threshold = p_threshold

    def sufficiently_cointegrated(self, ts_1, ts_2,):
        return self.p_value(ts_1, ts_2) < self.p_threshold

    def p_value(self, ts_1, ts_2):
        p = coint(ts_1, ts_2)[1]
        print('the p value is ', p)
        return p
