import sqlite3


class DBInterface:

    def __init__(self, db_path: str):
        # Establishing database connection
        self.db_path: str = db_path
        self.db_connection: sqlite3.Connection = sqlite3.connect(self.db_path, 10)
        self.db_connection.row_factory = sqlite3.Row  # Allows accessing column by name
        self.db_cursor: sqlite3.Cursor = self.db_connection.cursor()
        # Mandating foreign key constraint enforcement
        self._execute_query('PRAGMA foreign_keys = 1')

    def _execute_query(self,
                       sql_string: str,
                       parameters: tuple = None) -> tuple[int, dict]:
        """ Wrapper for cursor.execute """
        try:
            if parameters is None:
                self.db_cursor.execute(sql_string)
            else:
                self.db_cursor.execute(sql_string, parameters)
            return 0, {'success_mesage': 'Successfully executed query'}
        except sqlite3.Error as e:
            return -1, {'error_message': str(e)}

    def manual(self):
        """
            Debug fnx for manually manipulating the databse
        """
        sqlstring = """ SELECT * FROM stock_symbols """
        ret = self._execute_query(sqlstring)
        if ret[0] != 0:
            print("Problem running manual control")
            print(ret)
            exit(1)
        results = self.db_cursor.fetchall()
        for row in results:
            print(row['stock_symbol'])

    def seed_db(self) -> tuple[int, dict]:
        """ Responsible for initializing the database according to the desired schema.
            Will drop existing tables for fresh restart.
        """
        # Resetting existing db
        db_tables = [
            'historical_data',
            'wsb_posts',
            'symbol_post_junction',
            'stock_symbols'  # e.g. AAPL, TSLA
        ]
        for table in db_tables:
            sqlstring = f""" DROP TABLE IF EXISTS {table}"""
            ret = self._execute_query(sqlstring)
            if ret[0] != 0:
                print(f'Error dropping SQL table {table}')
                print(ret)
                exit(1)

        sqlstring = """ CREATE TABLE stock_symbols ( stock_symbol TEXT NOT NULL PRIMARY KEY )
                    """
        ret = self._execute_query(sqlstring)
        if ret[0] != 0:
            # Error
            return ret
        # Date is a UNIX timestamp
        sqlstring = """ CREATE TABLE historical_data (
                            stock_symbol TEXT NOT NULL,
                            date INTEGER NOT NULL,
                            open REAL NOT NULL,
                            close REAL NOT NULL,
                            high REAL NOT NULL,
                            low REAL NOT NULL,
                            volume INTEGER,
                            FOREIGN KEY(stock_symbol) REFERENCES stock_symbols(stock_symbol)
                        )
                    """
        ret = self._execute_query(sqlstring)
        if ret[0] != 0:
            return ret

        sqlstring = """ CREATE TABLE wsb_posts (
                            post_id TEXT NOT NULL PRIMARY KEY,
                            author TEXT NOT NULL,
                            title TEXT NOT NULL,
                            text TEXT,
                            hyperlink TEXT NOT NULL,
                            flair TEXT,
                            awards INTEGER NOT NULL,
                            upvote_ratio REAL NOT NULL,
                            comment_count INTEGER NOT NULL
                        )
                    """
        ret = self._execute_query(sqlstring)
        if ret[0] != 0:
            return ret
        sqlstring = """ CREATE TABLE symbol_post_junction (
                            post_id TEXT NOT NULL,
                            stock_symbol TEXT NOT NULL,
                            FOREIGN KEY(post_id) REFERENCES wsb_posts,
                            FOREIGN KEY(stock_symbol) REFERENCES stock_symbols
                            )
                    """
        ret = self._execute_query(sqlstring)
        if ret[0] != 0:
            return ret
        self.db_connection.commit()
        return 0, {'success_message': 'Successfully seeded db'}

    def insert_symbol(self, stock_symbol: str) -> tuple[int, dict]:
        sqlstring = """ INSERT INTO stock_symbols
                        VALUES (?)
                    """
        ret = self._execute_query(sqlstring, (stock_symbol,))
        if ret[0] == 0:
            self.db_connection.commit()
        return ret

    def populate_data(self,
                      stock_symbol: str,
                      date: float,
                      open_price: float,
                      close_price: float,
                      high_price: float,
                      low_price: float,
                      volume: int) -> tuple[int, dict]:
        """ Inserts historical data rows for the given stock symbol """

        sqlstring: str = """ INSERT INTO historical_data
                             VALUES (?, ?, ?, ?, ?, ?, ?)
                         """
        ret = self._execute_query(sqlstring, (stock_symbol,
                                              date,
                                              open_price,
                                              close_price,
                                              high_price,
                                              low_price,
                                              volume))
        if ret[0] == 0:
            self.db_connection.commit()
        return ret

    def naked_symbols(self) -> tuple[int, dict]:
        """ Returns stock symbols for which no data exists in the historical_data table """
        sqlstring = """ SELECT * FROM stock_symbols ss
                        WHERE ss.stock_symbol not in (SELECT stock_symbol FROM historical_data)
                    """
        ret = self._execute_query(sqlstring)
        if ret[0] != 0:
            return ret
        results: list = self.db_cursor.fetchall()
        symbol_list: list = []
        for row in results:
            symbol_list.append(row['stock_symbol'])
        return 0, {'content': symbol_list}

    def insert_post(self,
                    other_args):
        ...