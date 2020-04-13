import logging
import psycopg2 as db
import mysql
import sqlite3

TIMEOUT = 20  # seconds

conn_args = {
    'database': 'mysql_test',
    'user': 'root',
    'passwd': 'password',
    'host': 'localhost',
    'port': 3306,
    'connect_timeout': TIMEOUT,
}


class Mysql(object):
    def __init__(self, **conn_args):
        try:
            self.conn = mysql.connector.connect(**conn_args)

        except:
            self.log.error('Connection failed after %s seconds', str(TIMEOUT))
            raise

        self.cur = self.conn.cursor()
        self.conn_open = True
        self.cur_open = True

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def __del__(self):
        self.close()

    def query(self, query, params={}):
        self.cur.execute(query, params)

        # Don't commit on SELECT
        if 'SELECT' in query.upper():
            return self.cur.fetchall()

        # INSERT, UPDATE, DELETE, etc.
        self.conn.commit()

        # If returning string exists, fetch and return rows
        if 'RETURNING' in query.upper():
            return self.cur.fetchall()

    def close(self):
        if self.cur_open is True:
            self.cur.close()
            self.cur_open = False

        if self.conn_open is True:
            self.conn.close()
            self.conn_open = False
