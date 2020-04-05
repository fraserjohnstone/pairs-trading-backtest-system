class AssetService:
    def all(self):
        return [
            # 'DSHBTC', # Dash
            # 'BATBTC', # Basic Authentication Token
            'BABBTC', # Bitcoin Cash
            # 'EOSBTC', # EOS
            # 'QTMBTC', # Qtum
            # 'ETCBTC', # Etherium Classic
            # 'ETHBTC', # Entherium
            # 'LTCBTC', # Litecoin
            # 'XLMBTC', # Stellar Lumens
            # 'XMRBTC', # Monero
            # 'ZECBTC', # ZCash
            # 'XTZBTC', # Tezos
            'XRPBTC' # Ripple
        ]

    def possible_pairs(self):
        pairs = []
        for asset_a in self.all():
            for asset_b in self.all():
                if not asset_a == asset_b:
                    pairs.append([asset_a, asset_b])
        return pairs
