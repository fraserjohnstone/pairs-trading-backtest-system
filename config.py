from db_connection_manager import DbConnectionManager

def assets():
    conn = DbConnectionManager().conn
    cursor = conn.cursor()
    cursor.execute('SELECT code FROM assets')
    codes = cursor.fetchall()
    return [code[0] for code in codes]
