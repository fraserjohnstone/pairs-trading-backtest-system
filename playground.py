import pickle
from backtest.services.pair_selection_service import PairSelectionService
import backtest.algorithm.model as algo


pickle_in = open("backtest/assets/XRPBTC|BABBTC.pickle","rb")
pairs = pickle.load(pickle_in)
pickle_in.close()

algo.run_test(pairs)
