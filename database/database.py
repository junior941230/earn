# 檔案用途：集中處理 SQLite；之後放自選股、設定、委託紀錄與成交紀錄保存。
import sqlite3


class Database:
    def __init__(self, db_path="database/earn.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def initTables(self):
        # 初始化資料表，例如自選股、設定、委託紀錄與成交紀錄等
        # 第一張表：清單本身
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS watchlists (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                name    TEXT NOT NULL UNIQUE,
                sortOrder   INTEGER NOT NULL
            )
        ''')

        # 第二張表：清單裡的股票
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS watchlist_items (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                watchlist_id INTEGER NOT NULL,
                symbol       TEXT    NOT NULL,
                FOREIGN KEY (watchlist_id) REFERENCES watchlists(id)
                    ON DELETE CASCADE,
                UNIQUE (watchlist_id, symbol)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL UNIQUE,
                value TEXT
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                status TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def add_watchlist(self, name):
        # 尋找有無重複名稱
        sortOrder = self.cursor.execute(
            'SELECT COUNT(*) FROM watchlists').fetchone()[0]
        if self.cursor.execute('SELECT id FROM watchlists WHERE name = ?', (name,)).fetchone():
            print(f"Watchlist '{name}' already exists.")
            return False
        self.cursor.execute(
            'INSERT INTO watchlists (name, sortOrder) VALUES (?, ?)', (name, sortOrder))
        self.conn.commit()
        # 回傳新建立的 watchlist 的 ID
        return self.cursor.lastrowid

    def add_watchlist_item(self, watchlist_id, symbol):
        # 先檢查該 watchlist_id 是否存在
        if not self.cursor.execute('SELECT id FROM watchlists WHERE id = ?', (watchlist_id,)).fetchone():
            print(f"Watchlist ID '{watchlist_id}' does not exist.")
            return False
        # 再檢查該 symbol 是否已在該 watchlist 中
        if self.cursor.execute('SELECT id FROM watchlist_items WHERE watchlist_id = ? AND symbol = ?', (watchlist_id, symbol)).fetchone():
            print(
                f"Symbol '{symbol}' already exists in watchlist ID '{watchlist_id}'.")
            return False
        self.cursor.execute(
            'INSERT INTO watchlist_items (watchlist_id, symbol) VALUES (?, ?)', (watchlist_id, symbol))
        self.conn.commit()

    def add_setting(self, key, value):
        self.cursor.execute('''
            INSERT INTO settings (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value
        ''', (key, value))
        self.conn.commit()

    def get_watchlists(self):
        self.cursor.execute('SELECT * FROM watchlists')
        return self.cursor.fetchall()

    def get_watchlistName(self, watchlist_id):
        self.cursor.execute(
            'SELECT name FROM watchlists WHERE id = ?', (watchlist_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_watchlist_items(self, watchlist_id):
        self.cursor.execute(
            'SELECT symbol FROM watchlist_items WHERE watchlist_id = ?', (watchlist_id,))
        return [row[0] for row in self.cursor.fetchall()]

    def rename_watchlist(self, watchlist_id, new_name):
        # 檢查新名稱是否已存在
        if self.cursor.execute('SELECT id FROM watchlists WHERE name = ?', (new_name,)).fetchone():
            print(f"Watchlist name '{new_name}' already exists.")
            return False
        self.cursor.execute(
            'UPDATE watchlists SET name = ? WHERE id = ?', (new_name, watchlist_id))
        self.conn.commit()
        return True

    def remove_watchlist(self, watchlist_id):
        self.cursor.execute(
            'DELETE FROM watchlists WHERE id = ?', (watchlist_id,))
        self.conn.commit()

    def remove_watchlist_item(self, watchlist_id, symbol):
        self.cursor.execute(
            'DELETE FROM watchlist_items WHERE watchlist_id = ? AND symbol = ?', (watchlist_id, symbol))
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()

    def check(self):
        self.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table';")
        tables = self.cursor.fetchall()
        print("Tables in the database:")
        for table in tables:
            print(table[0])


if __name__ == "__main__":
    db = Database("database/earn.db")
    db.initTables()
    db.add_watchlist("Tech Stocks")
    watchlist_names = db.get_watchlists()
    print("Existing watchlists:", watchlist_names)
    db.close()
