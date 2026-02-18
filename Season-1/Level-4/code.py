'''
Please note:

The first file that you should run in this level is tests.py for database creation, with all tests passing.
Remember that running the hack.py will change the state of the database, causing some tests inside tests.py
to fail.

If you like to return to the initial state of the database, please delete the database (level-4.db) and run 
the tests.py again to recreate it.
'''

import sqlite3
import os
from flask import Flask, request

### Unrelated to the exercise -- Starts here -- Please ignore
app = Flask(__name__)
@app.route("/")
def source():
    DB_CRUD_ops().get_stock_info(request.args["input"])
    DB_CRUD_ops().get_stock_price(request.args["input"])
    DB_CRUD_ops().update_stock_price(request.args["input"])
    DB_CRUD_ops().exec_multi_query(request.args["input"])
    DB_CRUD_ops().exec_user_script(request.args["input"])
### Unrelated to the exercise -- Ends here -- Please ignore

class Connect(object):

    def create_connection(self, path):
        connection = None
        try:
            connection = sqlite3.connect(path)
        except sqlite3.Error as e:
            print(f"ERROR: {e}")
        return connection

class Create(object):

    def __init__(self):
        con = Connect()
        try:
            path = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(path, 'level-4.db')
            db_con = con.create_connection(db_path)
            cur = db_con.cursor()

            table_fetch = cur.execute(
                '''
                SELECT name 
                FROM sqlite_master 
                WHERE type='table'AND name='stocks';
                ''').fetchall()

            if table_fetch == []:
                cur.execute(
                    '''
                    CREATE TABLE stocks
                    (date text, symbol text, price real)
                    ''')
                cur.execute(
                    "INSERT INTO stocks VALUES ('2022-01-06', 'MSFT', 300.00)")
                db_con.commit()

        except sqlite3.Error as e:
            print(f"ERROR: {e}")

        finally:
            db_con.close()

class DB_CRUD_ops(object):

    # retrieves all info about a stock symbol from the stocks table
    def get_stock_info(self, stock_symbol):
        db = Create()
        con = Connect()
        try:
            path = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(path, 'level-4.db')
            db_con = con.create_connection(db_path)
            cur = db_con.cursor()

            res = "[METHOD EXECUTED] get_stock_info\n"

            restricted_chars = ";%&^!#-"
            has_restricted_char = any([char in stock_symbol for char in restricted_chars])
            correct_number_of_single_quotes = stock_symbol.count("'") == 0

            res += "[QUERY] SELECT * FROM stocks WHERE symbol = '" + stock_symbol + "'\n"

            if has_restricted_char or not correct_number_of_single_quotes:
                res += "CONFIRM THAT THE ABOVE QUERY IS NOT MALICIOUS TO EXECUTE"
            else:
                # SECURITY FIX: Parameterized query
                cur.execute("SELECT * FROM stocks WHERE symbol = ?", (stock_symbol,))
                query_outcome = cur.fetchall()
                for result in query_outcome:
                    res += "[RESULT] " + str(result)
            return res

        except sqlite3.Error as e:
            print(f"ERROR: {e}")

        finally:
            db_con.close()

    # retrieves the price of a stock symbol from the stocks table
    def get_stock_price(self, stock_symbol):
        db = Create()
        con = Connect()
        try:
            path = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(path, 'level-4.db')
            db_con = con.create_connection(db_path)
            cur = db_con.cursor()

            res = "[METHOD EXECUTED] get_stock_price\n"
            safe_symbol = stock_symbol.split("'")[0]
            res += "[QUERY] SELECT price FROM stocks WHERE symbol = '" + safe_symbol + "'\n"

            # SECURITY FIX: Parameterized query with sanitized input
            cur.execute("SELECT price FROM stocks WHERE symbol = ?", (safe_symbol,))
            query_outcome = cur.fetchall()
            for result in query_outcome:
                res += "[RESULT] " + str(result) + "\n"
            return res

        except sqlite3.Error as e:
            print(f"ERROR: {e}")

        finally:
            db_con.close()

    # updates stock price
    def update_stock_price(self, stock_symbol, price):
        db = Create()
        con = Connect()
        try:
            path = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(path, 'level-4.db')
            db_con = con.create_connection(db_path)
            cur = db_con.cursor()

            if not isinstance(price, float):
                raise Exception("ERROR: stock price provided is not a float")

            res = "[METHOD EXECUTED] update_stock_price\n"
            res += "[QUERY] UPDATE stocks SET price = '%d' WHERE symbol = '%s'\n" % (price, stock_symbol)

            # SECURITY FIX: Parameterized query
            cur.execute("UPDATE stocks SET price = ? WHERE symbol = ?", (price, stock_symbol))
            db_con.commit()
            query_outcome = cur.fetchall()
            for result in query_outcome:
                res += "[RESULT] " + result
            return res

        except sqlite3.Error as e:
            print(f"ERROR: {e}")

        finally:
            db_con.close()

    # SECURITY NOTE: Redesigned to only support known safe query patterns
    # with fully parameterized execution. No raw SQL fallback.
    def exec_multi_query(self, query):
        db = Create()
        con = Connect()
        try:
            path = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(path, 'level-4.db')
            db_con = con.create_connection(db_path)
            cur = db_con.cursor()

            res = "[METHOD EXECUTED] exec_multi_query\n"
            for q in filter(None, query.split(';')):
                res += "[QUERY]" + q + "\n"
                q = q.strip()
                query_outcome = []
                # SECURITY FIX: Route to fully parameterized queries - no raw SQL fallback
                if q.upper().startswith("SELECT PRICE"):
                    cur.execute("SELECT price FROM stocks WHERE symbol = ?",
                                (q.split("'")[1],))
                    query_outcome = cur.fetchall()
                elif q.upper().startswith("SELECT *"):
                    cur.execute("SELECT * FROM stocks WHERE symbol = ?",
                                (q.split("'")[1],))
                    query_outcome = cur.fetchall()
                elif q.upper().startswith("UPDATE"):
                    symbol = q.split("'")[3]
                    price = float(q.split("'")[1])
                    cur.execute("UPDATE stocks SET price = ? WHERE symbol = ?",
                                (price, symbol))
                db_con.commit()
                for result in query_outcome:
                    res += "[RESULT] " + str(result) + " "
            return res

        except sqlite3.Error as e:
            print(f"ERROR: {e}")

        finally:
            db_con.close()

    # SECURITY NOTE: Redesigned to only support known safe query patterns
    # with fully parameterized execution. No raw SQL fallback.
    def exec_user_script(self, query):
        db = Create()
        con = Connect()
        try:
            path = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(path, 'level-4.db')
            db_con = con.create_connection(db_path)
            cur = db_con.cursor()

            res = "[METHOD EXECUTED] exec_user_script\n"
            res += "[QUERY] " + query + "\n"
            query_outcome = []
            # SECURITY FIX: Route to fully parameterized queries - no raw SQL fallback
            if query.upper().startswith("SELECT PRICE"):
                cur.execute("SELECT price FROM stocks WHERE symbol = ?",
                            (query.split("'")[1],))
                query_outcome = cur.fetchall()
            elif query.upper().startswith("SELECT *"):
                cur.execute("SELECT * FROM stocks WHERE symbol = ?",
                            (query.split("'")[1],))
                query_outcome = cur.fetchall()
            elif query.upper().startswith("UPDATE"):
                symbol = query.split("'")[3]
                price = float(query.split("'")[1])
                cur.execute("UPDATE stocks SET price = ? WHERE symbol = ?",
                            (price, symbol))
            db_con.commit()
            for result in query_outcome:
                res += "[RESULT] " + str(result)
            return res

        except sqlite3.Error as e:
            print(f"ERROR: {e}")

        finally:
            db_con.close()
