import sqlite3

# @TODO Descriptive text for each tuple?
# @TODO add the full name of the company in table stock_symbols e.g. Microsoft


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
        sqlstring = """  SELECT * FROM historical_data
                        
                   """
        ret = self._execute_query(sqlstring)
        if ret[0] != 0:
            print("Problem running manual control")
            print(ret)
            exit(1)

        results = self.db_cursor.fetchall()
        return 0, {'content': results}

        # self.db_connection.commit()

    def pull_table(self, table: str) -> tuple[int, dict]:
        sqlstring: str = f""" SELECT * FROM  {table}"""
        ret = self._execute_query(sqlstring)
        if ret[0] != 0:
            return ret
        results: list = self.db_cursor.fetchall()
        return 0, {'content': results}

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

        sqlstring = """ CREATE TABLE stock_symbols ( stock_symbol TEXT NOT NULL PRIMARY KEY,
                                                     corp_name TEXT NOT NULL )
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
                            author_fullname TEXT NOT NULL,
                            upvote_ratio REAL NOT NULL,
                            comment_count INTEGER NOT NULL,
                            url TEXT NOT NULL,
                            award_count INTEGER NOT NULL,
                            post_title TEXT NOT NULL,
                            post_content TEXT,
                            timestamp REAL NOT NULL
                        )
                    """
        ret = self._execute_query(sqlstring)
        if ret[0] != 0:
            return ret
        sqlstring = """ CREATE TABLE symbol_post_junction (
                            post_id TEXT NOT NULL,
                            stock_symbol TEXT NOT NULL,
                            PRIMARY KEY (post_id, stock_symbol),
                            FOREIGN KEY(post_id) REFERENCES wsb_posts,
                            FOREIGN KEY(stock_symbol) REFERENCES stock_symbols
                            )
                    """
        ret = self._execute_query(sqlstring)
        if ret[0] != 0:
            return ret
        self.db_connection.commit()
        return 0, {'success_message': 'Successfully seeded db'}

    def insert_symbol(self,
                      stock_symbol: str,
                      corp_name: str) -> tuple[int, dict]:
        sqlstring = """ INSERT INTO stock_symbols
                        VALUES (?, ?)
                    """
        ret = self._execute_query(sqlstring,
                                  (stock_symbol, corp_name))
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

    def symbol_list(self) -> tuple[int, dict]:
        """ Returns the list of stock symbols """

        sqlstring: str = """ SELECT * FROM stock_symbols
                         """
        ret = self._execute_query(sqlstring)
        if ret[0] != 0:
            return ret
        results: list = self.db_cursor.fetchall()
        symbol_list: list = []
        for row in results:
            symbol_list.append(row['stock_symbol'])
        return 0, {'content': symbol_list}

    def prune_symbol(self, symbol: str) -> tuple[int, dict]:
        sqlstring: str = """ DELETE FROM stock_symbols
                             WHERE stock_symbol = (?)
                         """
        ret = self._execute_query(sqlstring, (symbol,))
        if ret[0] == 0:
            self.db_connection.commit()
        return ret

    def insert_post(self, post: dict) -> tuple[int, dict]:
        """ Takes a 'listing' object as returned from the reddit API. Includes a 'included_symbols' key
            whose value is a list of strings.
        """
        # Pulling out raw post information first
        post_id: str = post['data']['name']                        # Encoded ID of the post
        author: str = post['data']['author']                    # Uses the encoded name
        author_fullname: str = post['data']['author_fullname']  # Encoded ID used by the API
        upvote_ratio: float = post['data']['upvote_ratio']
        comm_count: int = post['data']['num_comments']
        url: str = post['data']['permalink']
        award_count: int = post['data']['total_awards_received']
        post_title: str = post['data']['title']
        post_content: str = post['data']['selftext']
        timestamp: float = post['data']['created']
        # Inserting values
        sqlstring: str = """ INSERT INTO wsb_posts
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                         """
        ret = self._execute_query(sqlstring, (post_id,
                                              author,
                                              author_fullname,
                                              upvote_ratio,
                                              comm_count,
                                              url,
                                              award_count,
                                              post_title,
                                              post_content,
                                              timestamp))
        if ret[0] != 0:
            return ret

        # Ingesting the symbol information now
        included_symbols: list = post['included_symbols']
        for symbol in included_symbols:
            # Update the post_symbol_junction table with entries.
            sqlstring = """ INSERT INTO symbol_post_junction
                            VALUES (?, ?)
                        """
            ret = self._execute_query(sqlstring, (post_id,
                                                  symbol))
            if ret[0] != 0:
                return -1, {'error_message': f'Failed to update symbol for post {post_id} {post_title}: {ret[1]}'}
        # Successfully added all post elements to the database
        self.db_connection.commit()
        return 0, {'success_message': f'Post {post_id} successfully commited to the database'}