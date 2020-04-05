import pickle
from backtest.services.pair_selection_service import PairSelectionService
from backtest.algorithm.model import Model


pickle_in = open("backtest/assets/XRPBTC|BABBTC.pickle","rb")
pairs = pickle.load(pickle_in)
pickle_in.close()

Model(pairs).backtest()
