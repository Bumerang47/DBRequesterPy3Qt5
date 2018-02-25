import sqlite3
import psycopg2
import mysql.connector
from pathlib import Path
import re


class DbAdapException(Exception):
    # Exception type for warning message same and to any type base
    def __init__(self, errno, msg, *errors):
        Exception.__init__(self, msg)
        self.errno = errno if errno else None
        self.msg = msg


class DbAdap:
    """
    Universal adapter for connection DB
    """

    def __init__(self, conn, dbtype='sqlite'):
        try:
            if dbtype == 'sqlite':
                if isinstance(conn, str) and len(conn) > 0:
                    if conn.find(':memory:') >= 0:
                        self.conn = sqlite3.connect(str(conn), uri = True)
                    else:
                        self.conn = sqlite3.connect(str(conn))
                else:
                    raise DbAdapException(msg='Invalid path connection DB', errno="Bad path")
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
            raise DbAdapException(errno, msg)
        self._complete = False

    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
        self.close()

    def complete(self):
        self._complete = True

    def close(self):
        if self.conn:
            try:
                if self._complete:
                    self.conn.commit()
                else:
                    self.conn.rollback()
            except Exception as e:
                raise DbAdapException(*e.args)
            finally:
                try:
                    self.conn.close()
                except Exception as e:
                    raise DbAdapException(*e.args)
