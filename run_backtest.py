from services.pair_selection_service import PairSelectionService
from backtest.algorithm.model import Model

pairs = PairSelectionService().selected_pairs(1, '1m')
Model(pairs).backtest()
