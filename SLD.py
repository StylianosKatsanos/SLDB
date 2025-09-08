# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 10:02:42 2025

@author: stkats
"""

import tkinter as tk 
from tkinter import ttk, messagebox, filedialog
import sqlite3
import pathlib
from SLD_line_input import SLD_Setup
from DB_creator import ask_name

# Paths to the root of the project.
PROJECT_ROOT = pathlib.Path(__file__).parent.resolve()
DB_ROOT = PROJECT_ROOT / 'test.db'

# ------------------- Non essential functions -----------------------------------#

def create_dict(pl_list: []):
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

###-------------------- LabelFrame to Host the Treeview Widget --------------------------###


class TreeviewFrame(tk.Frame):
    def __init__(self, root, project=DB_ROOT):
        
        self.root = root
        self.project = project

        super().__init__(self.root)
        
        fr = ttk.LabelFrame(root, text='SLD')
        fr.pack(fill='both', expand="yes")
        f = ttk.Frame(root)
        f.pack(fill='x', expand='yes', side='bottom')
        
        treeview = TreeviewSLD(fr, self.project)
        create_button = tk.Button(f, text='New DB', command=lambda: ask_name(tk.Toplevel()))
        create_button.pack(side="left")
        project_button = tk.Button(f, text='Select Project', command=treeview.select_project)
        project_button.pack(side="left")
        refresh_button = tk.Button(f, text='Refresh', command=treeview.refresh_tree)
        refresh_button.pack(side="left")
        #export_button = tk.Button(f, text='Export Report')
        #export_button.pack(side="left")
        line_button = tk.Button(f, text='Add line', command=treeview.initial_wind)
        line_button.pack(side="left")
        #mult_button = tk.Button(f, text='Mult', command=treeview.execute_mult_db_query('''SELECT Entry_name FROM Relationships WHERE Type = ?''', (('HV',),('Main',),('Plot',))))
        
        
        treeview.pack(fill=tk.BOTH, expand=True)
        treeview.heading("#0", text="Plant")
        
        #print(treeview.execute_db_query(treeview.first_query).fetchall())
        
        treeview.mainloop()
        
###-------------------- Treeview Widget for SLD -----------------------------------------###

class TreeviewSLD(ttk.Treeview):
    def __init__(self, master, db=(), plant='', **kw):
        
        if db == None:
            print("No SQLite database")
            return
        
        self.sld = None
        self.plant = plant
        self.database = db
        self.first_query = '''SELECT * FROM Relationships;'''
        self.entries_drop = self.all_entries()
        
        super().__init__(master, **kw)
        
        self.bind("<Double-1>", self.on_double_click)
        self.bind("<Button-3>", self.open_context_menu)
        self.context_menu = tk.Menu(master, tearoff=0)
        self.context_menu.add_command(label = "Info" , command=self.option_info)
        self.context_menu.add_separator()
        self.context_menu.add_command(label = "Attach" , command=self.option_attach)
        self.context_menu.add_command(label = "Edit" , command=self.option_edit)
        self.context_menu.add_separator()
        self.context_menu.add_command(label = "Delete" , command=self.option_delete)
        
        #self.refresh_tree()
        
        
###-------------- Code used for collection and organisation of data in Treeview --------------------------------------###
    
    def refresh_tree(self):
        refresh_query = '''SELECT * FROM ''' + '''Relationships'''
        data = self.execute_db_query(refresh_query).fetchall()
        tree_data = self.create_dict(pl_list=data)
        if self.get_children() == ():
            self.iterate_dict(tree_data)
        else:
            self.delete(self.get_children()[0])
            self.iterate_dict(tree_data)
        
    
    def all_entries(self):
        
        entries_query = '''SELECT Type,Entry_name FROM Relationships ORDER BY Type;'''
        data = self.execute_db_query(entries_query).fetchall()
        #data = [i[0] for i in data]
        entries = {}
        for pairs in data:
            if pairs[0] not in entries.keys():
                entries[pairs[0]] = []
                entries[pairs[0]].append(pairs[1])
            else:
                entries[pairs[0]].append(pairs[1])
        return entries
                          
    
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
        self.all_entries()
        print(self.selected_iid)   
        
    def option_attach(self):
        
        self.selected_iid = self.focus() 
        attached_to = self.item(self.selected_iid).get('text')
        
        self.transient = tk.Toplevel()
        self.transient.title("Attach Entry")
        self.transient.geometry("300x100")
        
        ttk.Label(self.transient, text="Give Entry Name:").grid(row=0, column=1)
        new_entry_widget = ttk.Entry(self.transient)
        new_entry_widget.grid(row=0,column=2)
        ttk.Label(self.transient, text="Attached To:").grid(row=1, column=1)
        atk = ttk.Entry(self.transient)
        atk.insert(0,attached_to)
        atk.grid(row=1, column=2)
        
        self.update_button = tk.Button(self.transient, text='Attach Entry', 
           command=lambda: self.insert_entry(new_entry_widget.get(), atk.get())).grid(row=3, column=1, sticky="n")
    

    def insert_entry(self,a,b):
        att_query = '''INSERT INTO Relationships (Entry_name, Attached_to) VALUES (?,?)'''
        pars = (a,b)
        if b not in self.all_entries():
            print("Not applicable entry to attach to")
            return
        self.execute_db_query(att_query, pars)
        self.insert(parent=b, index='end', iid=a, text=a)
            
    def option_edit(self):
        self.selected_iid = self.focus()
        
        old_entry = self.selected_iid
        old_att = self.parent(old_entry)
        
        self.transient = tk.Toplevel()
        self.transient.title("Edit Entry")
        self.transient.geometry("300x100")
        
        ttk.Label(self.transient, text="Entry Name:").grid(row=0, column=1)
        new_entry_widget = ttk.Entry(self.transient, textvariable = tk.StringVar(self.transient, value = self.selected_iid), width=20)
        new_entry_widget.insert('end',self.selected_iid)
        new_entry_widget.grid(row=0, column=2)
        ttk.Label(self.transient, text="Attached To:").grid(row=1, column=1)
        atk = ttk.Combobox(self.transient, state='readonly', values=[x for x in self.entries_drop if x != old_entry], width=17)
        atk.grid(row=1, column=2)
        atk.set(old_att)
        
        self.update_button = tk.Button(self.transient, text= 'Edit Entry',
            command=lambda: self.modify_entry(old_entry, old_att, new_entry_widget.get(), atk.get())).grid(row=3, column=1, sticky="n")
        
    def modify_entry(self, old_a: str, old_b: str, a: str,b: str):
        edit_query = '''UPDATE Relationships SET Entry_name=? WHERE Entry_name=?'''
        edit_att_query = '''UPDATE Relationships SET Attached_to=? WHERE Entry_name=?'''
        parsa = (a, old_a)
        parsb = (b, a)
        if b == "Start":
            self.start = tk.Toplevel()
            ttk.Label(self.start, text="Cannot modify entry named Start")
            return
        self.execute_db_query(edit_query, parsa)
        self.execute_db_query(edit_att_query, parsb)
        #self.item(b, text=a)
        self.refresh_tree()
        
    def option_delete(self):
        res = messagebox.askquestion(title="Delete Entry", message="Are you sure you want to delete this entry and everything that is attached to it?", type="yesno")
        if res == 'no':
            return
        else:
            delete_query = '''DELETE FROM Relationships where Entry_name= ?'''
            self.execute_db_query(delete_query, (self.selected_iid,))
            self.delete(self.selected_iid) 
            del_attached_query = '''DELETE FROM Relationships where Attached_to= ?'''
            self.execute_db_query(del_attached_query, (self.selected_iid,))
            #self.refresh_tree()
         
    
    def select_project(self):

        file_path = filedialog.askopenfilename(
            title= "Select a Database",
            initialdir=PROJECT_ROOT,
            filetypes=(("Databases", "*.db"), ("All files", "*.*"))
        )

        if file_path == '':
            return
        else:
            self.database = file_path
            self.plant = file_path.split('/')[-1].split('.')[0]
            self.heading("#0", text=self.plant)
            self.refresh_tree()
            
  
    def initial_wind(self):
    
        if self.plant == '' and self.sld == None:
            return
        else:
            init_win = tk.Toplevel()
            SLD_Setup((init_win),self.sld, self.add_new_line)
                     
    def add_new_line(self, entries):
        
        #types = ["HV", "Plot", "Main", "Skid", "Transformers", "LVPanels", "Inverters", "CircuitBreakers", "Strings"]
        #for_string_names = ["Skid", "Transformer", "LVPanel", "CircuitBreaker", "Inverter"]
        
        entries = [i for i in entries if i[1]]
        string_name = []
        parameters = []
        string_parameters = []
        last_entry_before_strings = ''
        
        # Lists are created so: [Type, Check, Name, New Name] - for Strings [Type, Check, Number of Strings]
        
        for e,i in enumerate(entries):
            # for any entries other than strings
            if i[0] != "Strings":

                if i[2] == 'New':
                    if e == 0:
                        parameters.append((i[3], 'Start', i[0]))
                    elif entries[e-1][2] == 'New':
                        parameters.append((i[3], entries[e-1][3], i[0]))
                    else:
                        parameters.append((i[3], entries[e-1][2], i[0]))
                    string_name.append(i[3].replace(i[0] + '_', '')) # Add another if for string applicable entries
                    last_entry_before_strings = i[3]
                else:
                    string_name.append(i[2].replace(i[0] + '_', '')) # Add another if for string applicable entries
                    last_entry_before_strings = i[2]

            # only for strings        
            else:
                if i[1] == False:
                    return
                number_of_strings = i[-1]
                name_base = '_'.join(string_name)
                string_list = ["String_" + name_base + "_" + str(i) for i in range(1,number_of_strings+1)] # list comprehension create all string names by joining base name with a number
                string_parameters = list(zip(string_list, [last_entry_before_strings] * len(string_list),["String"] * len(string_list)))
        
        if parameters:
            self.execute_mult_db_query('''Insert INTO Relationships (Entry_name, Attached_to, Type) VALUES (?,?,?)''', parameters)
        if string_parameters:
            self.execute_mult_db_query('''Insert INTO Relationships (Entry_name, Attached_to, Type) VALUES (?,?,?)''', string_parameters)
        self.refresh_tree()
    
###------------------- General SQLite Query Execution Command ----------------------------------------###

    def execute_db_query(self, query, parameters=()):
        with sqlite3.connect(self.database) as conn:
            cursor = conn.cursor()
            query_result = cursor.execute(query, parameters)
            conn.commit()
        return query_result


    def execute_mult_db_query(self, query, parameters=()):
        with sqlite3.connect(self.database) as conn:
            cursor = conn.cursor()
            query_result = map(lambda x: cursor.execute(query, x), parameters)
            print([i.fetchall() for i in query_result])
            conn.commit()
        return query_result


###------------------- Initial Setup of Database -----------------------------------------------------###

        

     
if __name__ == "__main__":
    
    db_ = DB_ROOT   
       
    root = tk.Tk()
    root.title('Treeview Demo - Hierarchical Data')
    root.geometry('400x300')
    
    label = TreeviewFrame(root)
    label.mainloop()
    
