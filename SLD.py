# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 10:02:42 2025

@author: stkats
"""

import tkinter as tk 
from tkinter import ttk
import sys
import sqlite3
import pathlib

# Paths to the root of the project.
PROJECT_ROOT = pathlib.Path(__file__).parent.resolve()
DB_ROOT = PROJECT_ROOT / 'Projects.db'

# ------------------- Non essential functions -----------------------------------#

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

def create_dict2(pl_dict={}, pl_list=[], keyword="Start"):
    for e, i in enumerate(pl_list):
        if i[1] == keyword:
            pl_dict[i[0]] = {}
            create_dict2(pl_dict[i[0]], pl_list, i[0])
        else:
            continue
    return pl_dict


###-------------------- Treeview Widget for SLD -----------------------------------------###

class TreeviewSLD(ttk.Treeview):
    def __init__(self, master, db=(), **kw):
        
        if db == None:
            print("No SQLite database")
            return
        
        self.database = db
        self.first_query = '''SELECT * FROM Relationships;'''
        
        super().__init__(master, **kw)
        
        self.bind("<Double-1>", self.on_double_click)
        self.bind("<Button-3>", self.open_context_menu)
        self.context_menu = tk.Menu(master, tearoff=0)
        self.context_menu.add_command(label = "Info" , command=self.option_info)
        self.context_menu.add_separator()
        self.context_menu.add_command(label = "Attach" , command=self.option_attach)
        self.context_menu.add_command(label = "Edit" , command=self.option_edit)
        self.context_menu.add_command(label = "Delete" , command=self.option_delete)
        
        self.refresh_tree()
        
        
###-------------- Code used for collection and organisation of data in Treeview --------------------------------------###
    
    def refresh_tree(self):
        data = self.execute_db_query(self.first_query).fetchall()
        tree_data = self.create_dict(pl_list=data)
        if self.get_children() == ():
            self.iterate_dict(tree_data)
        else:
            self.delete(self.get_children()[0])
            self.iterate_dict(tree_data)
        
    
    def all_children(self):
        if self.get_children() == ():
            return children
        else:
            output.append(self.get_children()[0])
            self.all_children(self.get_children()[1], children)
        pass
                          
    
    def create_dict(self, pl_dict={}, pl_list=[], keyword="Start"):
        for e, i in enumerate(pl_list):
            if i[1] == keyword:
                pl_dict[i[0]] = {}
                create_dict2(pl_dict[i[0]], pl_list, i[0])
            else:
                continue
        return pl_dict
    
    def iterate_dict(self,d, k=''):
        for key, value in d.items():
            #yield key
            self.insert(k, 'end', key, text=key)
            if isinstance(value, dict):
                #yield from self.iterate_dict(value, key)
                self.iterate_dict(value, key)
            else:
                p = key
                for j in sorted(list(value)):
                    #yield j
                    self.insert(p, 'end', j, text=j)

###-------------------------------- Options of Treeview -----------------------------------------------------------###

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
        self.all_children()
        print(self.selected_iid)   
        
    def option_attach(self):
        
        self.selected_iid = self.focus() 
        attached_to = self.item(self.selected_iid).get('text')
        
        self.transient = tk.Toplevel()
        self.transient.title("Attach Entry")
        self.transient.geometry("300x150")
        
        ttk.Label(self.transient, text="Give Entry Name:").grid(row=0, column=1)
        new_entry_widget = ttk.Entry(self.transient)
        new_entry_widget.grid(row=0,column=2)
        ttk.Label(self.transient, text="Attached To:").grid(row=1, column=1)
        atk = ttk.Entry(self.transient)
        atk.insert(0,attached_to)
        atk.config(state='readonly')
        atk.grid(row=1, column=2)
        
        self.update_button = ttk.Button(self.transient, text='Attach Entry', 
           command=lambda: self.insert_entry(new_entry_widget.get(), atk.get())).grid(row=3, column=1, sticky="n")
        
        seperator = ttk.Separator(self.transient, orient='horizontal')
        seperator.grid(row=4, columnspan=5, pady=5, padx=5, sticky='ew')
        
        ttk.Label(self.transient, text="Give Entry Name:").grid(row=5, column=1)
        new_entry_widget = ttk.Entry(self.transient)
        new_entry_widget.grid(row=5,column=2)
        ttk.Label(self.transient, text="Attached To:").grid(row=6, column=1)
        atk = ttk.Entry(self.transient)
        atk.insert(0,attached_to)
        atk.config(state='readonly')
        atk.grid(row=6, column=2)
        
        
    
    def insert_entry(self, a,b):
        att_query = '''INSERT INTO Relationships (Entry_name, Attached_to) VALUES (?,?)'''
        pars = (a,b)
        self.execute_db_query(att_query, pars)
        self.insert(parent=b, index='end', iid=a)
        self.refresh_tree()
            
    def option_edit(self):
        self.selected_iid = self.focus()
        print(self.get_children())
        
        self.transient = tk.Toplevel()
        self.transient.title("Edit Entry")
        self.transient.geometry("300x100")
        
        ttk.Label(self.transient, text="New Entry Name:").grid(row=0, column=1)
        new_entry_widget = ttk.Entry(self.transient)
        new_entry_widget.grid(row=0, column=2)
        ttk.Label(self.transient, text="Old Entry Name:").grid(row=1, column=1)
        atk = ttk.Entry(self.transient)
        atk.insert(0, self.selected_iid)
        atk.config(state='readonly')
        atk.grid(row=1, column=2)
        
        self.update_button = ttk.Button(self.transient, text= 'Edit Entry',
            command=lambda: self.modify_entry(new_entry_widget.get(), self.selected_iid)).grid(row=3, column=1, sticky="n")
        
    def modify_entry(self, a,b):
        edit_query = '''UPDATE Relationships SET Entry_name=? WHERE Entry_name=?'''
        edit_att_query = '''UPDATE Relationships SET Attached_to=? WHERE Attached_to=?'''
        pars = (a,b)
        print(pars)
        return
        if b == "Start":
            self.start = tk.Toplevel()
            ttk.Label(self.start, text="Cannot modify entry named Start")
            return
        self.execute_db_query(edit_query, pars)
        self.execute_db_query(edit_att_query, pars)
        #self.item(b, text=a)
        self.refresh_tree()
        pass
        
    def option_delete(self):
        delete_query = '''DELETE FROM Relationships where Entry_name= ?'''
        self.execute_db_query(delete_query, (self.selected_iid,))
        self.delete(self.selected_iid) 
        del_attached_query = '''DELETE FROM Relationships where Attached_to= ?'''
        self.execute_db_query(delete_query, (self.selected_iid,))
        #self.refresh_tree()


###------------------- General SQLite Query Execution Command ----------------------------------------###

    def execute_db_query(self, query, parameters=()):
        with sqlite3.connect(self.database) as conn:
            cursor = conn.cursor()
            query_result = cursor.execute(query, parameters)
            conn.commit()
        return query_result

     
if __name__ == "__main__":
    
    db_ = DB_ROOT   
    
#     plant = {
#         "HV":{
#             "Plot A":{
#                 "Main A1":{
#                     "Skid 1",
#                     "Skid 2",
#                     "Skid 3"
#                     },
#                 "Main A2":{}
#                 },
#             "Plot B":{
#                 "Main B1":{}, 
#                 "Main B2":{}
#                 }
#             }
#         }
        
    root = tk.Tk()
    root.title('Treeview Demo - Hierarchical Data')
    root.geometry('400x200')
    
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    
    treeview = TreeviewSLD(root, db_)
    treeview.pack(fill=tk.BOTH, expand=True)
    treeview.heading("#0", text="Plant")
     
    treeview.mainloop()
