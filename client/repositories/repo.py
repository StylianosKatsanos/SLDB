# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 17:24:00 2026

@author: stkats
"""

import sqlite3

class SQLiteRepo:
    """SQLite helper matching the original execute_db_query behavior."""

    def __init__(self, db_filename: str):
        self.db_filename = db_filename

    def execute(self, query: str, params=()):
        with sqlite3.connect(self.db_filename) as conn:
            cur = conn.cursor()
            res = cur.execute(query, params)
            conn.commit()
            return res

    def fetchall(self, query: str, params=()):
        return self.execute(query, params).fetchall()