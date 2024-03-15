# sqlite_override.py
from pysqlite3 import dbapi2 as sqlite3

# Import everything from pysqlite3 into this module's namespace
from pysqlite3.dbapi2 import *
