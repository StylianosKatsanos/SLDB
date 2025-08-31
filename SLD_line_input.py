# -*- coding: utf-8 -*-
"""
Created on Sat Jun 21 11:47:31 2025

@author: Admin
"""

import tkinter as tk 
from tkinter import ttk

class SLD_Setup:
    def __init__(self, root, sld, func):
        
        init_win = root
        init_win.geometry("700x350")
        
        self.func = func
        self.sld = sld
        self.parts = ["HV","Plot","Main","Skid","Transformer","LVPanel","CircuitBreaker","Inverter"]
        
        fr = tk.LabelFrame(init_win, text="SLD Setup")
        fr.pack(fill='both', expand="yes")
        
        tk.Label(fr, text='HV:', relief="groove", padx=5, pady=5, width=15).grid(row=1, column=1)
        tk.Label(fr, text='Plot:', relief="groove", padx=5, pady=5, width=15).grid(row=2, column=1)
        tk.Label(fr, text='Main:', relief="groove", padx=5, pady=5, width=15).grid(row=3, column=1)
        tk.Label(fr, text='Skid:', relief="groove", padx=5, pady=5, width=15).grid(row=4, column=1)
        tk.Label(fr, text='Transformer:', relief="groove", padx=5, pady=5, width=15).grid(row=5, column=1)
        tk.Label(fr, text='LV Panel:', relief="groove", padx=5, pady=5, width=15).grid(row=6, column=1)
        tk.Label(fr, text='Circuit Breaker:', relief="groove", padx=5, pady=5, width=15).grid(row=7, column=1)
        tk.Label(fr, text='Inverter:', relief="groove", padx=5, pady=5, width=15).grid(row=8, column=1)
        tk.Label(fr, text='String:', relief="groove", padx=5, pady=5, width=15).grid(row=9, column=1)
        
        self.hv = tk.BooleanVar()
        self.plot = tk.BooleanVar()
        self.main = tk.BooleanVar()
        self.skid = tk.BooleanVar()
        self.trans = tk.BooleanVar()
        self.lv = tk.BooleanVar()
        self.inv = tk.BooleanVar()
        self.cb = tk.BooleanVar()
        self.string = tk.BooleanVar()
        
        self.check_vars = [self.hv, self.plot,self.main,self.skid, self.trans, self.lv, self.inv, self.cb, self.string]
        
        self.hv_items = tk.StringVar()
        self.plot_items = tk.StringVar()
        self.main_items = tk.StringVar()
        self.skid_items = tk.StringVar()
        self.trans_items = tk.StringVar()
        self.lv_items = tk.StringVar()
        self.inv_items = tk.StringVar()
        self.cb_items = tk.StringVar()
        
        
        self.text_vars = [self.hv_items, self.plot_items, self.main_items, self.skid_items, self.trans_items, self.lv_items, self.inv_items, self.cb_items]
        
        
        hv_check = tk.Checkbutton(fr, variable=self.hv ,onvalue=True, offvalue=False)
        hv_check.grid(row=1, column=2)
        plot_check = tk.Checkbutton(fr, variable=self.plot, onvalue=True, offvalue=False)
        plot_check.grid(row=2, column=2)
        main_check = tk.Checkbutton(fr, variable=self.main,onvalue=True, offvalue=False)
        main_check.grid(row=3, column=2)
        skid_check = tk.Checkbutton(fr, variable=self.skid,onvalue=True, offvalue=False)
        skid_check.grid(row=4, column=2)
        trans_check = tk.Checkbutton(fr, variable=self.trans,onvalue=True, offvalue=False)
        trans_check.grid(row=5, column=2)
        lv_check = tk.Checkbutton(fr, variable=self.lv,onvalue=True, offvalue=False)
        lv_check.grid(row=6, column=2)
        inv_check = tk.Checkbutton(fr, variable=self.inv, onvalue=True, offvalue=False)
        inv_check.grid(row=7, column=2)
        cb_check = tk.Checkbutton(fr, variable=self.cb , onvalue=True, offvalue=False)
        cb_check.grid(row=8, column=2)
        str_check = tk.Checkbutton(fr, variable=self.string , onvalue=True, offvalue=False)
        str_check.grid(row=9, column=2)
        
        self.spins = []
        self.name_entries = []
        
        # Add parts that are not in the original sld not to have dictionary key errors
        for i in self.parts:
            if i not in self.sld.keys():
                self.sld[i] = []
        
        #--------------------------- HV ---------------------------------------#
        self.hv_spin = tk.ttk.Combobox(fr, textvariable=self.hv_items, values= ["New"] + self.sld["HV"])
        self.hv_spin.grid(row=1, column=3, sticky='w')
        tk.Label(fr, text='New Name:', padx=5).grid(row=1, column=4)
        self.hv_name = tk.Entry(fr,width=20)
        self.hv_name.grid(row=1,column=5)
        self.spins.append(self.hv_spin)
        self.name_entries.append(self.hv_name)
        
        #--------------------------- Plot --------------------------------------#
        self.plot_spin = tk.ttk.Combobox(fr, textvariable=self.plot_items, values= ["New"] + self.sld["Plot"])
        self.plot_spin.grid(row=2, column=3, sticky='w')
        tk.Label(fr, text='New Name:', padx=5).grid(row=2, column=4)
        self.plot_name = tk.Entry(fr,width=20)
        self.plot_name.grid(row=2,column=5)
        self.spins.append(self.plot_spin)
        self.name_entries.append(self.plot_name)
        
        #--------------------------- Main --------------------------------------#
        self.main_spin = tk.ttk.Combobox(fr, textvariable=self.main_items, values= ["New"] + self.sld["Main"])
        self.main_spin.grid(row=3, column=3, sticky='w')
        tk.Label(fr, text='New Name:', padx=5).grid(row=3, column=4)
        self.main_name = tk.Entry(fr,width=20)
        self.main_name.grid(row=3,column=5)
        self.spins.append(self.main_spin)
        self.name_entries.append(self.main_name)
        
        #--------------------------- Skid --------------------------------------#
        self.skid_spin = tk.ttk.Combobox(fr, textvariable=self.skid_items, values= ["New"] + self.sld["Skid"])
        self.skid_spin.grid(row=4, column=3, sticky='w')
        tk.Label(fr, text='New Name:', padx=5).grid(row=4, column=4)
        self.skid_name = tk.Entry(fr,width=20)
        self.skid_name.grid(row=4,column=5)
        self.spins.append(self.skid_spin)
        self.name_entries.append(self.skid_name)
        
        #--------------------------- Transformer --------------------------------------#
        self.trans_spin = tk.ttk.Combobox(fr, textvariable=self.trans_items, values= ["New"] + self.sld["Transformer"])
        self.trans_spin.grid(row=5, column=3, sticky='w')
        tk.Label(fr, text='New Name:', padx=5).grid(row=5, column=4)
        self.trans_name = tk.Entry(fr,width=20)
        self.trans_name.grid(row=5,column=5)
        self.spins.append(self.trans_spin)
        self.name_entries.append(self.trans_name)
        
        #--------------------------- LV Panels --------------------------------------#
        self.lv_spin = tk.ttk.Combobox(fr, textvariable=self.lv_items, values= ["New"] + self.sld["LVPanel"])
        self.lv_spin.grid(row=6, column=3, sticky='w')
        tk.Label(fr, text='New Name:', padx=5).grid(row=6, column=4)
        self.lv_name = tk.Entry(fr,width=20)
        self.lv_name.grid(row=6,column=5)
        self.spins.append(self.lv_spin)
        self.name_entries.append(self.lv_name)
        
        #--------------------------- Circuit Breakers --------------------------------------#
        self.cb_spin = tk.ttk.Combobox(fr, textvariable=self.cb_items, values= ["New"] + self.sld["CircuitBreaker"])
        self.cb_spin.grid(row=7, column=3, sticky='w')
        tk.Label(fr, text='New Name:', padx=5).grid(row=7, column=4)
        self.cb_name = tk.Entry(fr,width=20)
        self.cb_name.grid(row=7,column=5)
        self.spins.append(self.cb_spin)
        self.name_entries.append(self.cb_name)
        
        #--------------------------- Inverters --------------------------------------#
        self.inv_spin = tk.ttk.Combobox(fr, textvariable=self.inv_items, values= ["New"] + self.sld["Inverter"])
        self.inv_spin.grid(row=8, column=3, sticky='w')
        tk.Label(fr, text='New Name:', padx=5).grid(row=8, column=4)
        self.inv_name = tk.Entry(fr,width=20)
        self.inv_name.grid(row=8,column=5)
        self.spins.append(self.inv_spin)
        self.name_entries.append(self.inv_name)

        #--------------------------- Strings --------------------------------------#
        tk.Label(fr, text='Number of strings:', padx=5).grid(row=9, column=3)
        self.str_spin = tk.Spinbox(fr, from_=0, to=100, width=5)
        self.str_spin.grid(row=9, column=4, sticky='w')
        self.spins.append(self.str_spin)
        
        
        self.initial_button = tk.Button(fr, text="Setup", command = self.pass_new_line)
        self.initial_button.grid(row=10, column=1, padx=5, pady=5)
        
        init_win.mainloop()
        
    def get_all_checks(self)->list:
        line_data = []
        checks_better = list(map(lambda x: x.get(),self.check_vars))
        allspin = list(map(lambda x: x.get(), self.spins))
        all_names = list(map(lambda x: x.get(), self.name_entries))
        all_names.append('end')
        line_data.append(self.parts)
        line_data.append(checks_better)
        line_data.append(allspin)
        line_data.append(all_names)
        final = list(zip(line_data[0], line_data[1], line_data[2], line_data[3]))
        final.append(["Strings", self.string.get(), int(self.str_spin.get())])
        return final
    
    def pass_new_line(self):
        self.func(self.get_all_checks())
        

                
class manual_input:
    
    def __init__(self, root, func, entry):
        
        win = root
        win.geometry("400x300")
        win.title("Give manually the names of the entries")
        
        self.add = tk.LabelFrame(win, text="Manual Inputs")
        self.add.pack(fill='both', expand="no")
        
        self.func = func
        self.entry = entry
        
        see = tk.LabelFrame(win, text="List of Inputs Inputs")
        see.pack(fill='both', expand="yes", side='bottom')
        
        self.input_entry = tk.Entry(self.add,width=40)
        self.input_entry.pack(expand="yes",side="left")
        add_button = tk.Button(self.add, text="Add Entry", command=self.insert_entry)
        add_button.pack(side="left")
        
        self.entries_list = tk.Listbox(see)
        self.entries_list.pack(expand="yes",fill="both")
        delete_button = tk.Button(see, text="Delete Entry", command= self.delete_entry)
        delete_button.pack(side="bottom")
        
        export_button = tk.Button(self.add, text="Export Entries", command= self.Parentfunc)
        export_button.pack(side="right")
        
        win.mainloop()
        
    def insert_entry(self):
        new_entry = self.input_entry.get()
        self.entries_list.insert('end', new_entry)
        self.input_entry.delete('0',tk.END)
        
    def delete_entry(self):
        
        item_delete = self.entries_list.curselection()
        if item_delete == ():
            return
        else:
            self.entries_list.delete(item_delete)
    
    def Parentfunc(self):
        self.func(self.entries_list.get(0,'end'), self.entry)
            

if __name__ == "__main__":
    
    test_schema = {"HV":["HV1","HV2"],
                   "Plot":[],
                   "Main":[],
                   "Skid":[],
                   "Transformers":[],
                   "LVPanels":[],
                   "Inverters":[],
                   "CircuitBreakers":[]
                   }
    
    SLD_Setup(tk.Tk(), test_schema, lambda x: print(x))