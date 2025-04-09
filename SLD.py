# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 10:02:42 2025

@author: stkats
"""

import tkinter as tk 
from tkinter import ttk
import sys
import sqlite3

def execute_db_query(filename, query, parameters=()):
    with sqlite3.connect(filename) as conn:
        cursor = conn.cursor()
        query_result = cursor.execute(query, parameters)
        conn.commit()
    return query_result

def create_dict(pl_list):
    pl_dict = {}
    for i in pl_list:
        if i[1] == "Start":
            pl_dict[i[0]] = {}
            print("Start Found")
            print(pl_dict)
        else:
            if i[1] in pl_dict.keys():
                pl_dict[i[1]][i[0]] = {} 
                print("Key Found")
                print(pl_dict)
    return pl_dict.items()

class TreeviewEdit(ttk.Treeview):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        
        self.bind("<Double-1>", self.on_double_click)
        self.bind("<Button-3>", self.open_context_menu)
        self.context_menu = tk.Menu(master, tearoff=0)
        self.context_menu.add_command(label = "Info" , command=self.option_info)
        self.context_menu.add_separator()
        self.context_menu.add_command(label = "Attach" , command=self.option_attach)
        self.context_menu.add_command(label = "Edit" , command=self.option_edit)
        self.context_menu.add_command(label = "Delete" , command=self.option_delete)
        
        
    def on_double_click(self, event):
        
        self.selected_iid = self.focus() 
        selected_items = self.item(self.selected_iid)
        return(selected_items.get('text'))

    def open_context_menu(self,event):
        
        self.selected_iid = self.focus()
        self.context_menu.tk_popup(event.x_root, event.y_root)
        return
    
    def option_info(self):
        if self.selected_iid == "":
            return
        print(self.selected_iid)   
        
    def option_attach(self):
        pass
    
    def option_edit(self):
        pass
        
    def option_delete(self):
        pass

    def iterate_dict(self,d, k=''):
        for key, value in d.items():
            yield key
            self.insert(k, 'end', key, text=key)
            if isinstance(value, dict):
                yield from self.iterate_dict(value, key)
            else:
                p = key
                for j in sorted(list(value)):
                    yield j
                    self.insert(p, 'end', j, text=j)
                    

        
if __name__ == "__main__":
    
    query = '''SELECT * FROM Relationships;'''
    
    a = execute_db_query(db_, query).fetchall()
    b = create_dict(a)
    
    sys.exit()
    
    plant = {
        "HV":{
            "Plot A":{
                "Main A1":{
                    "Skid 1",
                    "Skid 2",
                    "Skid 3"
                    },
                "Main A2":{}
                },
            "Plot B":{
                "Main B1":{}, 
                "Main B2":{}
                }
            }
        }
        
    root = tk.Tk()
    root.title('Treeview Demo - Hierarchical Data')
    root.geometry('400x200')
    
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    
    
    treeview = TreeviewEdit(root)
    treeview.pack(fill=tk.BOTH, expand=True)
    treeview.heading("#0", text="Plant")
    
    for x in treeview.iterate_dict(plant):
        print(x)

    
    treeview.mainloop()
