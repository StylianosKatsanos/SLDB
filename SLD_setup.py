# -*- coding: utf-8 -*-
"""
Created on Sat Jun 21 11:47:31 2025

@author: Admin
"""

import tkinter as tk 


class SLD_Setup:
    def __init__(self, root):
        
        init_win = root
        init_win.geometry("600x300")
        
        fr = tk.LabelFrame(init_win, text="SLD Setup")
        fr.pack(fill='both', expand="yes")
        
        tk.Label(fr, text='HV:', relief="groove", padx=5, pady=5, width=15).grid(row=1, column=1)
        tk.Label(fr, text='Plot:', relief="groove", padx=5, pady=5, width=15).grid(row=2, column=1)
        tk.Label(fr, text='Main:', relief="groove", padx=5, pady=5, width=15).grid(row=3, column=1)
        tk.Label(fr, text='Skid:', relief="groove", padx=5, pady=5, width=15).grid(row=4, column=1)
        tk.Label(fr, text='LV Panel:', relief="groove", padx=5, pady=5, width=15).grid(row=5, column=1)
        tk.Label(fr, text='Inverter:', relief="groove", padx=5, pady=5, width=15).grid(row=6, column=1)
        tk.Label(fr, text='Circuit Breaker:', relief="groove", padx=5, pady=5, width=15).grid(row=7, column=1)
        tk.Label(fr, text='String:', relief="groove", padx=5, pady=5, width=15).grid(row=8, column=1)
        
        
        self.hv = tk.BooleanVar()
        self.plot = tk.BooleanVar()
        self.main = tk.BooleanVar()
        self.skid = tk.BooleanVar()
        self.lv = tk.BooleanVar()
        self.inv = tk.BooleanVar()
        self.cb = tk.BooleanVar()
        self.string = tk.BooleanVar()
        
        hv_check = tk.Checkbutton(fr, variable=self.hv ,onvalue=True, offvalue=False, command=self.change_states)
        hv_check.grid(row=1, column=2)
        plot_check = tk.Checkbutton(fr, variable=self.plot, onvalue=True, offvalue=False, command=self.change_states)
        plot_check.grid(row=2, column=2)
        main_check = tk.Checkbutton(fr, variable=self.main,onvalue=True, offvalue=False, command=self.change_states)
        main_check.grid(row=3, column=2)
        skid_check = tk.Checkbutton(fr, variable=self.skid,onvalue=True, offvalue=False, command=self.change_states)
        skid_check.grid(row=4, column=2)
        lv_check = tk.Checkbutton(fr, variable=self.lv,onvalue=True, offvalue=False, command=self.change_states)
        lv_check.grid(row=5, column=2)
        inv_check = tk.Checkbutton(fr, variable=self.inv, onvalue=True, offvalue=False, command=self.change_states)
        inv_check.grid(row=6, column=2)
        cb_check = tk.Checkbutton(fr, variable=self.cb , onvalue=True, offvalue=False, command=self.change_states)
        cb_check.grid(row=7, column=2)
        str_check = tk.Checkbutton(fr, variable=self.string ,onvalue=True, offvalue=False, command=self.change_states)
        str_check.grid(row=8, column=2)
        
        self.hv_button = tk.Button(fr, text="HV Names:", state="disabled", command=self.create_input)
        self.hv_button.grid(row=1, column=3)
        hv_entry = tk.Entry(fr, width=30)
        hv_entry.grid(row=1, column=4, padx=5)
        
        self.plot_button = tk.Button(fr, text="Plot Names:", state="disabled", command=self.create_input)
        self.plot_button.grid(row=2, column=3)
        plot_entry = tk.Entry(fr, width=30)
        plot_entry.grid(row=2, column=4, padx=5)
        
        tk.Label(fr, text='Number of values:', padx=5).grid(row=3, column=3)
        tk.Label(fr, text='Number of values:', padx=5).grid(row=4, column=3)
        tk.Label(fr, text='Number of values:', padx=5).grid(row=5, column=3)
        tk.Label(fr, text='Number of values:', padx=5).grid(row=6, column=3)
        tk.Label(fr, text='Number of values:', padx=5).grid(row=7, column=3)
        tk.Label(fr, text='Number of values:', padx=5).grid(row=8, column=3)
        
        self.main_spin = tk.Spinbox(fr, from_=1, to=100, width=5, state="disabled")
        self.main_spin.grid(row=3, column=4, sticky='w')
        self.skid_spin = tk.Spinbox(fr, from_=1, to=100, width=5, state="disabled")
        self.skid_spin.grid(row=4, column=4, sticky='w')
        self.lv_spin = tk.Spinbox(fr, from_=1, to=100, width=5, state="disabled")
        self.lv_spin.grid(row=5, column=4, sticky='w')
        self.inv_spin = tk.Spinbox(fr, from_=1, to=100, width=5, state="disabled")
        self.inv_spin.grid(row=6, column=4, sticky='w')
        self.cb_spin = tk.Spinbox(fr, from_=1, to=100, width=5, state="disabled")
        self.cb_spin.grid(row=7, column=4, sticky='w')
        self.str_spin = tk.Spinbox(fr, from_=1, to=100, width=5, state="disabled")
        self.str_spin.grid(row=8, column=4, sticky='w')
        
        init_win.mainloop()
        
    def get_all_checks(self)->list: 
        checks = [self.hv.get(), self.plot.get(), self.main.get(), self.skid.get(), self.lv.get(), self.inv.get(), self.cb.get(), self.string.get()]
        return checks
    
    def change_states(self):
        levels = self.get_all_checks()
        states = [self.hv_button,self.plot_button,self.main_spin,self.skid_spin,self.lv_spin,self.inv_spin,self.cb_spin,self.str_spin]
        for e,i in enumerate(levels):
            if i == True:
                states[e].config(state="normal")
            else:
                states[e].config(state="disabled")
                
    def create_input(self):
        win = tk.Toplevel()
        manual_input(win)

                
class manual_input:
    
    def __init__(self, root):
        
        win = root
        win.geometry("400x300")
        win.title("Give manually the names of the entries")
        
        add = tk.LabelFrame(win, text="Manual Inputs")
        add.pack(fill='both', expand="no")
        
        see = tk.LabelFrame(win, text="List of Inputs Inputs")
        see.pack(fill='both', expand="yes", side='bottom')
        
        self.input_entry = tk.Entry(add,width=40)
        self.input_entry.pack(expand="yes",side="left")
        add_button = tk.Button(add, text="Add Entry", command= lambda: self.entries_list.insert('end', self.input_entry.get()))
        add_button.pack(side="left")
        
        self.entries_list = tk.Listbox(see)
        self.entries_list.pack(expand="yes",fill="both")
        delete_button = tk.Button(see, text="Delete Entry", command= self.delete_entry)
        delete_button.pack(side="bottom")
        
        export_button = tk.Button(add, text="Export Entries", command= self.export_entries)
        export_button.pack(side="right")
        
        win.mainloop()
        
        
    def delete_entry(self):
        
        item_delete = self.entries_list.curselection()
        if item_delete == ():
            return
        else:
            self.entries_list.delete(item_delete)
            
    
    def export_entries(self):
        entries = self.entries_list.get(0,'end')
        return entries    
            

if __name__ == "__main__":
    
    SLD_Setup(tk.Tk())