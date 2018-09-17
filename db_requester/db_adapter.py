import sqlite3
import psycopg2
import mysql.connector
import re


class DbAdapterException(Exception):
    """ Exception type for warning message same and to any type base """

    def __init__(self, error, msg, *errors):
        Exception.__init__(self, msg)
        self.error = error if error else None
        self.msg = msg


class DbAdapter:
    """ Universal adapter for connection DB """

    def __init__(self, conn, dbtype='sqlite'):
        try:
            if dbtype == 'sqlite':
                if isinstance(conn, str) and len(conn) > 0:
                    if conn.find(':memory:') >= 0:
                        self.conn = sqlite3.connect(str(conn), uri=True)
                    else:
                        self.conn = sqlite3.connect(str(conn))
                else:
                    raise DbAdapterException(msg='Invalid path connection DB', errno="Bad path")
            elif dbtype == 'postgresql':
                self.conn = psycopg2.connect(conn)
            elif dbtype == 'mysql':
                # mysql connection take only to arguments of divided format.
                # So we splitting string with connecting
                params = {}
                for item in re.split(r'(?<=[\']|["]), |,| ', conn):
                    key, val = item.split('=')
                    _val = re.sub('(^[\'|"])|([\'|"]$)', '', val)
                    params.update({key: _val})

                self.conn = mysql.connector.connect(**params)
        except Exception as e:
            msg = e.msg if 'msg' in dir(e) else e.args[0]
            errno = e.errno if 'errno' in dir(e) else None
            raise DbAdapterException(errno, msg)
