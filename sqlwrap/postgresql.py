import os
import logging
import psycopg2 as db
from typing import List
TIMEOUT = 20  # seconds


class PostgreSQL(object):
    conn = None
    cur = None

    def __init__(self, **conn_args):
        self.log = logging.getLogger(__name__)
        self.statuses = ['SELECT', 'INSERT', 'DELETE', 'UPDATE']

        # conn_args = self.handle_conn_args(conn_args)

        try:
            self.conn = db.connect(**conn_args)

        except db.Error as e:
            self.log.error('Connection failed after %s seconds', str(conn_args['connect_timeout']))
            raise Exception(e)

        self.cur = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def __del__(self):
        self.close()

    def query(self, query: str, params={}: dict) -> List[tuple]:
        try:
            self.cur.execute(query, params)

            if any(s in self.cur.statusmessage for s in self.statuses):
                # Don't commit on SELECT
                if 'SELECT' in self.cur.statusmessage:
                    return self.fetch_rows()

                # INSERT, UPDATE, DELETE, etc.
                self.conn.commit()

                self.log.debug('Commit Success')

                # If returning string exists, fetch and return rows
                if 'RETURNING' in query.upper():
                    return self.fetch_rows()

            else:
                self.log.error('DB cursor statusmessage not in: %s',
                               str(self.statuses))

        except db.OperationalError as e:
            self.log.error('OperationError Raised: %s', str(e))
            raise

        except db.ProgrammingError as e:
            self.log.error('ProgrammingError Raised: %s', str(e))
            raise

        return None

    def fetch_rows(self):
        if self.cur.rowcount > 0:
            return self.cur.fetchall()

        return None

    def check(self):
        if self.cur is None or self.conn is None:
            return

        if self.cur.closed is False:
            self.log.debug('Cursor: Open')
        else:
            self.log.debug('Cursor: Closed')

        if self.conn.closed == 0:
            self.log.debug('Connection: Open')
        else:
            self.log.debug('Connection: Closed')

    def close(self):
        if self.cur is None or self.conn is None:
            return

        if self.cur.closed is False:
            self.cur.close()

        if self.conn.closed == 0:
            self.conn.close()

    def handle_conn_args(self, conn_args):
        # Case 1: No input, default to ~/.pgpass file
        # Example: hostname:port:database:username:password
        if conn_args is None:
            # Check for non-standard location in ENV variables
            passfile = os.environ.get('PGPASSFILE', None)
            conn_args = self.connect_with_pgpass(passfile)

        # Case 2: No input, default to ENV variables
        if conn_args is None:
            host = os.environ.get('PGHOST', None)
            port = os.environ.get('PGPORT', None)
            database = os.environ.get('PGDATABASE', None)
            user = os.environ.get('PGUSER', None)
            password = os.environ.get('PGPASSWORD', None)

            conn_array = [host, port, database, user, password]

            if any(x is None for x in conn_array):
                raise Exception('Required connection arguments invalid or missing')

            conn_args = self.assemble_conn_args(conn_array)

        # Final Case: Raise exception because no input or default args are found
        if conn_args is None:
            raise Exception('Connection arguments not found')

        return conn_args

    def connect_with_pgpass(self, passfile=None):
        # Set default location to home folder
        if passfile is None:
            passfile = os.path.join(os.path.expanduser('~'), '.pgpass')

        if not os.path.isfile(passfile):
            self.log.error('No pgpass file found: %s', str(passfile))
            return None

        with open(passfile, 'r') as f:
            conn_string = f.read()
            conn_array = conn_string.split(':')
            conn_args = self.assemble_conn_args(conn_array)

        return conn_args

    def assemble_conn_args(self, conn_array):
        conn_args = {}
        pg_name_list = ['host', 'port', 'database', 'user', 'password']

        for i, key in enumerate(pg_name_list):
            conn_args[key] = conn_array[i]

        return conn_args




# conn_args = {
#     'database': PGSQL_DBNAME,
#     'user': PGSQL_USERNAME,
#     'password': PGSQL_PASSWORD,
#     'host': PGSQL_HOSTNAME,
#     'port': PGSQL_PORT,
#     'connect_timeout': 15,
# }