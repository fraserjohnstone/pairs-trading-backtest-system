from services.pair_selection_service import PairSelectionService
from services.asset_service import AssetService
import time

class CointegrationDetectionProcess:
    def __init__(self):
        self.asset_service = AssetService()
        self.pair_selection_service = PairSelectionService()

    def run(self):

        selected = self.pair_selection_service.selected_pairs(
            self.asset_service.all()
        )
