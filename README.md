# sqlwrap
Simple wrapper for various database libraries

## Purpose

The purpose of this library is to exploit common patterns in SQL queries in order to increase code readability and encourage proper connection handling.

This is done by adding a very thin abstraction layer that makes assumptions based on the input query.

We try to take a SQL first approach to writing queries. Many python libraries try to abstract the SQL logic away, but this encourages it.

Turns code like this:
``` python
import psycopg2 as db

q = """
    SELECT  first_name
    FROM    user
    LIMIT   10
"""

conn = db.connect(conn_args)
cur = conn.cursor()
cur.execute(q)
result = cur.fetchall()
cursor.close()
conn.close()
```

Into this:
``` python
from sqlwrap import postgresql

q = """
    SELECT  first_name
    FROM    user
    LIMIT   10
"""

with postgresql(conn_args) as db:
    result = db.query(q)
```


And code like this:
``` python
import psycopg2 as db

q = """
    UPDATE  user
    SET     first_name = 'Jane'
    WHERE   user_id = '1234'
"""

conn = db.connect(conn_args)
cur = conn.cursor()
cur.execute(q)
conn.commit()
cursor.close()
conn.close()
```

Into this:
``` python
from sqlwrap import postgresql

q = """
    UPDATE  user
    SET     first_name = 'Jane'
    WHERE   user_id = '1234'
"""

with postgresql(conn_args) as db:
    result = db.query(q)
```


And code like this:
``` python
import psycopg2 as db

q = """
    INSERT INTO user (first_name, last_name)
    VALUES ('Jane', 'Doe')
    RETURNING user_id
"""

conn = db.connect(conn_args)
cur = conn.cursor()
cur.execute(q)
conn.commit()
result = cur.fetchall()
cursor.close()
conn.close()
```

Into this:
``` python
from sqlwrap import postgresql

q = """
    INSERT INTO user (first_name, last_name)
    VALUES ('Jane', 'Doe')
    RETURNING user_id
"""

with postgresql(conn_args) as db:
    result = db.query(q)
```

### Examples

#### Connection

Connections are identical to whatever the wrapper DB layer is underneath.

``` python
conn_args = {
    'dbname': 'test_db',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': 5432
}
```

``` python
from sqlwrap import postgresql

q = """
    SELECT *
    FROM   public.user
    WHERE  first_name = 'Jane'
"""

# Example #1: Context manager
with postgresql(conn_args) as db:
    result = db.query(q)

# Example #2: Standard Class Object
db = postgresql(conn_args)
result = db.query(q)
db.close()

# Example #3: Inside of a class constructor
class User:
    def __init__(self):
        self.db = postgresql(conn_args)

    def __del__(self):
        self.db.close()

    def get_user_by_first_name(self, first_name):
        q = """
            SELECT *
            FROM   public.user
            WHERE  first_name = %(name)s
        """

        result = self.db.query(q)

    def get_user_by_name(self, name):
        q = """
            SELECT *
            FROM   public.user
            WHERE  first_name = %(name)s
        """

        result = self.db.query(q)
```
