# -*- coding: utf-8 -*-
"""
Created on Fri Nov 29 14:26:58 2024

@author: stkats
"""

import pandas as pd
import numpy as np
from tabulate import tabulate
import sys
import datetime
import sqlite3


def get_week(date):
    try:
        date = get_revision(date, -1)
        strp = datetime.datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return ("No correct form of Date")
    strp = strp.date()
    cal = strp.isocalendar()
    return cal.week

def get_year(date):
    try:
        date = get_revision(date, -1)
        strp = datetime.datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return ("No correct form of Date")
    strp = strp.date()
    cal = strp.isocalendar()
    return cal.year


def series_weeks(date):
    if len(date) > 6:
        year = get_year(date)
    else:
        year = date
    weeks = []
    for i in range(0, 53):
        w = "{0}/{1}".format(i+1,year)
        weeks.append(w)
    ser = pd.Series(data=weeks, name="Weeks")
    return ser
  

def execute_db_query(query, parameters=(), db=""):
    with sqlite3.connect(db) as conn:
        #print(conn)
        #print('You have successfully connected to the database and executed the query')
        #print(query)
        cursor = conn.cursor()
        query_result = cursor.execute(query, parameters)
        conn.commit()
    return query_result  

def get_planned(database):
    query = 'SELECT name FROM pragma_table_info("Projects");'

    results = execute_db_query(query, db=database)

    headers = []

    for i in results.fetchall():
        if "Planned" in i[0]:
            headers.append(i[0])
    return headers


def create_df(ser, headers):
    df = pd.DataFrame(ser)
    for i in headers:
        df["{}".format(i)] = ""
    df.set_index("Weeks", inplace=True)
    return df


def get_sql(database=''):
    planned_query = '''SELECT * FROM Projects;'''
    with sqlite3.connect(database) as conn:
        pland = pd.read_sql(planned_query, conn)
    headers = list(pland.columns.values)
    pland.drop(columns=headers[1:5], axis=1, inplace=True)
    pland.set_index("Project_Name", inplace=True)
    return  pland


def fill_schedule(sched, data):
    
    projects = list(data.index)
    plans = list(data.columns)[0::2]
    
    for e, i in enumerate(range(0,len(data.columns),2)):
        #a = np.empty([len(data.index)])
        #b = pd.Series(a)
        #w = data.iloc[:,i:i+2]
        
        
        list_plan = list(data.iloc[:,i])
        list_act = list(data.iloc[:,i+1])
        
        for j in range(0,len(list_plan)):
            
            #if list_plan[j] == None:
            #    continue
            #if list_act[j] != None:
            #    continue
            slot = schedule_conditions(list_plan[j], list_act[j])
            if  slot == None:
                continue
            else: 
                w = get_week(list_plan[j])
                y = get_year(list_plan[j])
            #print("{}/{}".format(w,y))
                w_y = "{}/{}".format(w,y)
                
                try:
                    sched.loc[w_y,plans[e]] += "\n" + projects[j] + ','
                except KeyError:
                        pass
    return sched

def schedule_conditions(plan, act):
    
    if plan == None:
        return None
    else:
        if act == None:
            return plan
        else:
            pc = plan.count("->")
            ac = act.count("->")
            if pc == ac:
                return None
            elif pc > ac:
                return plan
            else:
                return None


def get_revision(all_dates, pos):
    if "->" in all_dates:
        rev = all_dates.split("->")[pos]
    else:
        rev = all_dates
    return rev


def get_schedule(date, db):
    weekser = series_weeks(date)
    h = get_planned(db)
    j = create_df(weekser, h)
    a = get_sql(db)
    b = fill_schedule(j, a)
    #c = (tabulate(b, headers = 'keys', tablefmt = 'grid',stralign=("center")))
    
    return b
    


#t = "2024-06-14"

#get_schedule(t)

if __name__ == "__main__":

    weekser = series_weeks(t)
    h = get_planned()
    test = create_df(weekser, h)
    a = get_sql()

    b = fill_schedule(test, a)

#print(get_planned())


#------------------------------------------ Make table ------------------------------------------------------#

    c = (tabulate(b, headers = 'keys', tablefmt = 'grid',stralign=("center")))

#styled_a = a.style.background_gradient(cmap='viridis')

#print(a.to_string)
#a.to_excel('test.xlsx',sheet_name='test', index=False)




    with open('test2.txt', 'w') as f:
#    f.write(a.headers)
        f.write(c)