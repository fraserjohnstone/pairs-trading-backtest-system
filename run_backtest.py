from backtest.services.pair_selection_service import PairSelectionService
from backtest.algorithm.model import Model

pairs = PairSelectionService().selected_pairs()
Model(pairs).backtest()
