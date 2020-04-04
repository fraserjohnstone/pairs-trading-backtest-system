from db_connection_manager import DbConnectionManager

class AssetService:
    def __init__(self):
        self.db_conn = DbConnectionManager().conn

    def cursor(self):
        return

    def all(self):
        # cursor = self.db_conn.cursor()
        # cursor.execute('SELECT code FROM assets')
        # codes = cursor.fetchall()
        # return [code[0] for code in codes] + ['BTCGBP']
        return ['XRPBTC', 'BABBTC']

    def possible_pairs(self):
        # cursor = self.db_conn.cursor()
        # cursor.execute('SELECT * FROM possible_pairs')
        # rows = cursor.fetchall()
        # return [[row[1], row[2]] for row in rows]
        return [['XRPBTC', 'BABBTC'], ['BABBTC', 'XRPBTC']]
