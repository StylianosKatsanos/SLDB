# -*- coding: utf-8 -*-
"""
Created on Mon Jun 16 21:39:40 2025

@author: Admin
"""

import xlsxwriter as xl

# plant = {
#          "HV":{
#              "Plot A":{
#                  "Main A1":{
#                      "Skid 1",
#                      "Skid 2",
#                      "Skid 3"
#                      },
#                  "Main A2":{}
#                  },
#              "Plot B":{
#                  "Main B1":{}, 
#                  "Main B2":{}
#                  }
#              }
#          }

db = [('HV', 'Start'), 
      ('Plot_A', 'HV'), ('Plot_B', 'HV'), 
      ('Main_A1', 'Plot_A'), ('Main_A2', 'Plot_A'), ('Main_B1', 'Plot_B'), 
      ('Skid_1', 'Main_A1'), ('Skid_2', 'Main_A1'), ('Skid_3', 'Main_A1'), 
      ('Main_B2', 'Plot_B')]



# Create a workbook and add a worksheet.
workbook = xl.Workbook('Expenses01.xlsx')
worksheet = workbook.add_worksheet()

# Start from the first cell. Rows and columns are zero indexed.
row = 0
col = 0

worksheet.write(row, col, "Entry")
worksheet.write(row, col + 1, "Attached_to")
row += 1

for i in db:
    worksheet.write(row, 0, i[0])
    worksheet.write(row, 1, i[1])
    row += 1
    
workbook.close()
