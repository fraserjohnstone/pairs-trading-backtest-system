from services.pair_selection_service import PairSelectionService
import pickle
import applied_algorithm as algo


pickle_in = open("assets/XRPBTC|BABBTC.pickle","rb")
pairs = pickle.load(pickle_in)
pickle_in.close()

algo.run(pairs)
