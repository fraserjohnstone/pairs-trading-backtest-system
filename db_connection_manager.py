import mysql.connector
import json
import io

class DbConnectionManager:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host='localhost',
            user='fraser',
            passwd='Mancini2180',
            database='pairs-trading-backtest'
        )
