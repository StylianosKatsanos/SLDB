# -*- coding: utf-8 -*-
"""
Created on Sat Sep 06 2025

@author: stkats
"""

import sqlite3
import tkinter as tk
import pathlib

def ask_name(root):
    label = tk.Label(root, text="What is the name of the new database?")
    entry = tk.Entry(root)
    label.pack()
    entry.pack()
    button = tk.Button(root, text="New DB", command=lambda: createDB(entry.get()))
    button.pack()
    root.mainloop()


def createDB(name):

    if name == "":
        return

    conn = sqlite3.connect(str(name) + ".db")

    with conn:
        print('Database of project ' + str(name) + ' created')
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Relationships (
        Entry_name TEXT NOT NULL PRIMARY KEY UNIQUE,
        Attached_to TEXT REFERENCES Relationships (Entry_name),
        Type TEXT NOT NULL)
        ''')
        print("Table created successfully")


if __name__ == '__main__':
    root = tk.Tk()
    ask_name(root)