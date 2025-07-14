# -*- coding: utf-8 -*-
"""
Created on Sat Jun 21 11:47:31 2025

@author: Admin
"""

import tkinter as tk 


class SLD_Setup:
    def __init__(self, root):
        
        init_win = root
        init_win.geometry("700x350")
        
        fr = tk.LabelFrame(init_win, text="SLD Setup")
        fr.pack(fill='both', expand="yes")
        
        
        tk.Label(fr, text='Name:', relief="groove", padx=5, pady=5, width=15).grid(row=0, column=1)
        tk.Label(fr, text='HV:', relief="groove", padx=5, pady=5, width=15).grid(row=1, column=1)
        tk.Label(fr, text='Plot:', relief="groove", padx=5, pady=5, width=15).grid(row=2, column=1)
        tk.Label(fr, text='Main:', relief="groove", padx=5, pady=5, width=15).grid(row=3, column=1)
        tk.Label(fr, text='Skid:', relief="groove", padx=5, pady=5, width=15).grid(row=4, column=1)
        tk.Label(fr, text='Transformer:', relief="groove", padx=5, pady=5, width=15).grid(row=5, column=1)
        tk.Label(fr, text='LV Panel:', relief="groove", padx=5, pady=5, width=15).grid(row=6, column=1)
        tk.Label(fr, text='Inverter:', relief="groove", padx=5, pady=5, width=15).grid(row=7, column=1)
        tk.Label(fr, text='Circuit Breaker:', relief="groove", padx=5, pady=5, width=15).grid(row=8, column=1)
        tk.Label(fr, text='String:', relief="groove", padx=5, pady=5, width=15).grid(row=9, column=1)
        
        self.name = tk.StringVar()
        self.hv = tk.BooleanVar()
        self.plot = tk.BooleanVar()
        self.main = tk.BooleanVar()
        self.skid = tk.BooleanVar()
        self.trans = tk.BooleanVar()
        self.lv = tk.BooleanVar()
        self.inv = tk.BooleanVar()
        self.cb = tk.BooleanVar()
        self.string = tk.BooleanVar()
        
        self.hvs = None
        self.plots = None
        
        self.name_entry = tk.Entry(fr, width=30)
        self.name_entry.grid(row=0, column=2, padx=5, columnspan=2)
        hv_check = tk.Checkbutton(fr, variable=self.hv ,onvalue=True, offvalue=False, command=self.change_states)
        hv_check.grid(row=1, column=2)
        plot_check = tk.Checkbutton(fr, variable=self.plot, onvalue=True, offvalue=False, command=self.change_states)
        plot_check.grid(row=2, column=2)
        main_check = tk.Checkbutton(fr, variable=self.main,onvalue=True, offvalue=False, command=self.change_states)
        main_check.grid(row=3, column=2)
        skid_check = tk.Checkbutton(fr, variable=self.skid,onvalue=True, offvalue=False, command=self.change_states)
        skid_check.grid(row=4, column=2)
        trans_check = tk.Checkbutton(fr, variable=self.trans,onvalue=True, offvalue=False, command=self.change_states)
        trans_check.grid(row=5, column=2)
        lv_check = tk.Checkbutton(fr, variable=self.lv,onvalue=True, offvalue=False, command=self.change_states)
        lv_check.grid(row=6, column=2)
        inv_check = tk.Checkbutton(fr, variable=self.inv, onvalue=True, offvalue=False, command=self.change_states)
        inv_check.grid(row=7, column=2)
        cb_check = tk.Checkbutton(fr, variable=self.cb , onvalue=True, offvalue=False, command=self.change_states)
        cb_check.grid(row=8, column=2)
        str_check = tk.Checkbutton(fr, variable=self.string ,onvalue=True, offvalue=False, command=self.change_states)
        str_check.grid(row=9, column=2)
        
        self.hv_button = tk.Button(fr, text="HV Names:", state="disabled", command= lambda: self.create_input(self.hv_entry))
        self.hv_button.grid(row=1, column=3)
        self.hv_entry = tk.Entry(fr, width=30)
        self.hv_entry.grid(row=1, column=4, padx=5, columnspan=2)
        
        self.plot_button = tk.Button(fr, text="Plot Names:", state="disabled", command= lambda: self.create_input(self.plot_entry))
        self.plot_button.grid(row=2, column=3)
        self.plot_entry = tk.Entry(fr, width=30)
        self.plot_entry.grid(row=2, column=4, padx=5, columnspan=2)
        
        tk.Label(fr, text='Number of values:', padx=5).grid(row=3, column=3)
        tk.Label(fr, text='Number of values:', padx=5).grid(row=4, column=3)
        tk.Label(fr, text='Number of values:', padx=5).grid(row=5, column=3)
        tk.Label(fr, text='Number of values:', padx=5).grid(row=6, column=3)
        tk.Label(fr, text='Number of values:', padx=5).grid(row=7, column=3)
        tk.Label(fr, text='Number of values:', padx=5).grid(row=8, column=3)
        tk.Label(fr, text='Number of values:', padx=5).grid(row=9, column=3)
        
        self.main_spin = tk.Spinbox(fr, from_=0, to=100, width=5, state="disabled")
        self.main_spin.grid(row=3, column=4, sticky='w')
        self.skid_spin = tk.Spinbox(fr, from_=0, to=100, width=5, state="disabled")
        self.skid_spin.grid(row=4, column=4, sticky='w')
        self.trans_spin = tk.Spinbox(fr, from_=0, to=100, width=5, state="disabled")
        self.trans_spin.grid(row=5, column=4, sticky='w')
        self.lv_spin = tk.Spinbox(fr, from_=0, to=100, width=5, state="disabled")
        self.lv_spin.grid(row=6, column=4, sticky='w')
        self.inv_spin = tk.Spinbox(fr, from_=0, to=100, width=5, state="disabled")
        self.inv_spin.grid(row=7, column=4, sticky='w')
        self.cb_spin = tk.Spinbox(fr, from_=0, to=100, width=5, state="disabled")
        self.cb_spin.grid(row=8, column=4, sticky='w')
        self.str_spin = tk.Spinbox(fr, from_=0, to=100, width=5, state="disabled")
        self.str_spin.grid(row=9, column=4, sticky='w')
        
        #------------  Main --------------------------------------#
        tk.Label(fr, text='Skids:', padx=2, pady=2, width=10).grid(row=3, column=5, sticky='w')
        self.main_skids = tk.Spinbox(fr, from_=0, to=100, width=5, state="disabled")
        self.main_skids.grid(row=3, column=6, sticky='w')
        
        tk.Label(fr, text='Transformers:', padx=2, pady=2, width=15).grid(row=3, column=7, sticky='w')
        self.main_trans = tk.Spinbox(fr, from_=0, to=100, width=5, state="disabled")
        self.main_trans.grid(row=3, column=8, sticky='w')
        
        #------------ Skid --------------------------------------------#
        tk.Label(fr, text='LV Panels:', padx=2, pady=2, width=10).grid(row=4, column=5, sticky='w')
        self.skid_lvs = tk.Spinbox(fr, from_=0, to=100, width=5, state="disabled")
        self.skid_lvs.grid(row=4, column=6, sticky='w')
        
        tk.Label(fr, text='Inverters:', padx=2, pady=2, width=15).grid(row=4, column=7, sticky='w')
        self.skid_invs = tk.Spinbox(fr, from_=0, to=100, width=5, state="disabled")
        self.skid_invs.grid(row=4, column=8, sticky='w')
        
        #------------ Transformer ----------------------------------------#
        tk.Label(fr, text='LV Panels:', padx=2, pady=2, width=10).grid(row=5, column=5, sticky='w')
        self.skid_lvs = tk.Spinbox(fr, from_=0, to=100, width=5, state="disabled")
        self.skid_lvs.grid(row=5, column=6, sticky='w')
        
        tk.Label(fr, text='Inverters:', padx=2, pady=2, width=15).grid(row=5, column=7, sticky='w')
        self.skid_invs = tk.Spinbox(fr, from_=0, to=100, width=5, state="disabled")
        self.skid_invs.grid(row=5, column=8, sticky='w')
        
        self.initial_button = tk.Button(fr, text="Setup", command = self.get_setup)
        self.initial_button.grid(row=10, column=1)
        
        init_win.mainloop()
        
    def get_all_checks(self)->list: 
        checks = [self.hv.get(), self.plot.get(), self.main.get(), self.skid.get(), self.trans.get(), self.lv.get(), self.inv.get(), self.cb.get(), self.string.get()]
        return checks
    
    def change_states(self):
        levels = self.get_all_checks()
        states = [[self.hv_button],[self.plot_button],[self.main_spin,self.main_skids, self.main_trans],[self.skid_spin],[self.trans_spin],[self.lv_spin],[self.inv_spin],[self.cb_spin],[self.str_spin]]
        for e,check in enumerate(levels):
            if check == True:
                if isinstance(states[e], list):
                    for i in states[e]:
                        i.config(state="normal")
                else:
                    states[e].config(state="normal")
            else:
                if isinstance(states[e], list):
                    for i in states[e]:
                        i.config(state="disabled")
                else:
                    states[e].config(state="disabled")
                
    
    def update_entry(self, data, entry_to_update):
        
        if entry_to_update == self.hv_entry:
            self.hvs = data
            text = ';'.join(data)
        elif entry_to_update == self.plot_entry:
            self.plots = data
            text = ';'.join(data)
        
        entry_to_update.delete("0", tk.END)
        entry_to_update.insert(tk.END,text)
        
    def create_input(self, to_update):
        win = tk.Toplevel()
        self.input_wind = manual_input(win, self.update_entry, to_update)
        
        
    def get_setup(self) -> list:
        print(self.hvs)
        pass
        

                
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
    
    SLD_Setup(tk.Tk())