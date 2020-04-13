from services.pair_selection_service import PairSelectionService
import json
import time

class CointegrationDetectionProcess:
    def __init__(self):
        self.pair_selection_service = PairSelectionService()

    def run(self):
        while True:
            pair_names = []
            selected_pairs = self.pair_selection_service.selected_pairs(
                1, '5m'
            )
            for pair in selected_pairs.keys():
                pair_names.append(pair)

            with open(self.results_path(), 'w', encoding='utf-8') as f:
                json.dump(pair_names, f, ensure_ascii=False, indent=4)
                
            time.sleep(5*60)

    def results_path(self):
        return 'processes/coint_results.json'
