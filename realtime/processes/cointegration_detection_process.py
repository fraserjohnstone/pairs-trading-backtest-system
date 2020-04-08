from realtime.services.pair_selection_service import PairSelectionService
from realtime.services.asset_service import AssetService
import time

class CointegrationDetectionProcess:
    def __init__(self):
        self.asset_service = AssetService()
        self.pair_selection_service = PairSelectionService()

    def run(self):
        while True:
            selected = self.pair_selection_service.selected_pairs()
            for key, value in selected.items():
                print(key)
