# Gestion de la base SQLite

import sqlite3
from sqlite3 import Connection, Cursor
from typing import Optional
from contextlib import contextmanager