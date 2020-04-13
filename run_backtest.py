from services.pair_selection_service import PairSelectionService
from models.backtest import Backtest
import pickle

with open("30_days_all_assets.pickle","rb") as f:
    all_pairs = pickle.load(f)

pairs = PairSelectionService().selected_from_pickled_candles(all_pairs)

Backtest().run(pairs)
