#excelscratchpad2.py

import pandas as pd
import random as rd

input_filepath = "../assets/GameFitStrategy.xlsx"
#cd Documents/GitHub/Math_Sim_v2/archive
columns="A:D"
# import the file
excel_file = pd.ExcelFile(input_filepath)


# # # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.ExcelFile.parse.html
###ExcelFile.parse(sheet_name=0, header=0, names=None, index_col=None, usecols=None, squeeze=None, converters=None, true_values=None, 
###false_values=None, skiprows=None, nrows=None, na_values=None, parse_dates=False, date_parser=None, thousands=None, comment=None, 
###skipfooter=0, convert_float=None, mangle_dupe_cols=True, **kwds)

# parse the first sheet
print(f"Found Sheets {excel_file.sheet_names}")   # to see the sheet names 
## this is a 'full game' - in that it needs all three sheets to function. 
sheet_count = 0
spin_sheet1 = excel_file.parse(sheet_name=sheet_count, usecols=columns, header=0)
spin_sheet1.columns = spin_sheet1.columns.str.strip()
sheet_count += 1
games_total = len(spin_sheet1)  # this is how many bonus games we have
print(f'{spin_sheet1} \nand we found {games_total} games, total')
#print(f"found {games_total} total games!")
lines_sheet1 = excel_file.parse(sheet_name=sheet_count, usecols=columns, header=0)
lines_sheet1.columns = lines_sheet1.columns.str.strip()
sheet_count += 1
print(f'{lines_sheet1}')
pays_sheet1 = excel_file.parse(sheet_name=sheet_count, usecols=columns, header=0)
pays_sheet1.columns = pays_sheet1.columns.str.strip()
sheet_count += 1
print(f'{pays_sheet1}')

# load a dynamic 'Tables' dataframe/dictionary(?) based on each set of 3 tables: spins, lines, pays
#bonus games counted by rows, (starts counting at 0, hence the b_g_t+1, and we are starting at 2 to skip the first 'main' row.)
# dynamically named, for the row number. so bonus_spin_sheet1, bonus_lines_sheet2, etc
for i in range(2, games_total+1):
   print(f"Loading Bonus Game sheet {i} at sheet_count {sheet_count}")
   exec("spin_sheet%d = excel_file.parse(sheet_name=sheet_count, usecols=columns, header=0)" % i)
   exec("spin_sheet%d.columns = spin_sheet%d.columns.str.strip()" % (i, i))
   #print(f'SPIN SHEET {i}:')
   exec("print(f'{spin_sheet%d}')" % i)
   sheet_count += 1
   exec("lines_sheet%d = excel_file.parse(sheet_name=sheet_count, usecols=columns, header=0)" % i)
   exec("lines_sheet%d.columns = lines_sheet%d.columns.str.strip()" % (i, i))
   #print(f"LINES SHEET {i}:")
   exec("print(f'{lines_sheet%d}')" % i)
   sheet_count += 1
   exec("pays_sheet%d = excel_file.parse(sheet_name=sheet_count, usecols=columns, header=0)" % i)
   exec("pays_sheet%d.columns = pays_sheet%d.columns.str.strip()" % (i, i))
   #print(f"PAYS SHEET {i}:")
   exec("print(f'{pays_sheet%d}')" % i)
   sheet_count += 1


def bonus_game(spin_sheet, lines_sheet, pays_sheet):
   # will use spin_sheet{sheet_num}. lines_sheet{sheet_num}, and pays_sheet{sheet_num}
   # this will heavily use the exec() function using the sheet_number
   #print(f"{spin_sheet}")
   #print(f"{lines_sheet}")
   #print(f"{pays_sheet}")
   random = rd.randrange(0, int(spin_sheet[-1:]['Upper Range']))
   print(f"   Bonus Spins: random: {random}")      
   for i, row in spin_sheet.iterrows():
      #print(f" -- spin check in bonus: checking row {i} with info {row}")
      if(random >= row["Lower Range"] and random <= row["Upper Range"]):
         spins = row[0]
         print(f"      Found {spins} Bonus spins")
         if(spins>0):
            for j in range(0, spins):
               random = rd.randrange(0, int(lines_sheet[-1:]['Upper Range']))
               print(f"      Bonus Lines: at spin {j} random: {random}")
               for l, lrow in lines_sheet.iterrows():
                  #print(f" -- lines check in bonus: checking {l} with info {lrow}")
                 if(random >= lrow["Lower Range"] and random <= lrow["Upper Range"]):
                     print(f"         Bonus Chose {lrow[0]} Line Wins")
                     if(lrow[0] > 0):
                        for lines in range(0, lrow[0]):  
                           random = rd.randrange(0, int(pays_sheet[-1:]['Upper Range']))
                           print(f"            Bonus Wins random: {random}")
                           for bw, bwrow in pays_sheet.iterrows():
                              if(random >= bwrow["Lower Range"] and random <= bwrow["Upper Range"]):
                                 print(f"               Bonus Winner! would add {bwrow[0]} to the total, found between {bwrow['Lower Range']} and {bwrow['Upper Range']}")
                                 
   #exec("" % sheet_num)

# the row will be the index of the sheet.  so we'll be having to exec(...% idx) to reference the lists
def play_game():
   # The "Game Spins".. if this were a slot, it would be the "play game" button. Will use spin_sheet1, lines_sheet1, and pays_sheet1
   # random number vs spin table.   ## set upper range as a variable, so we don't have to keep calling the data structure? 
   random = rd.randrange(0, int(spin_sheet1[-1:]['Upper Range']))
   print(f"Main Game Initial Bonus Trigger, randomly chosen, for the spin: {random}")
   for i, row in spin_sheet1.iterrows():
      if(random >= row["Lower Range"] and random <= row["Upper Range"]):
         print(f"   Found {random} is between {row['Lower Range']} and {row['Upper Range']}")
         if(i == 0):
            print(f"Playing Main Game")
            random = rd.randrange(0, int(lines_sheet1[-1:]['Upper Range']))
            print(f"   Main Game Lines: randomly chosen, for the lines: {random}")
            for l, lrow in lines_sheet1.iterrows():
               if(random >= lrow["Lower Range"] and random <= lrow["Upper Range"]):
                  print(f"      Chose {lrow[0]} Line Wins")
                  if(lrow[0] > 0):
                     for lines in range(0, lrow[0]):  
                        random = rd.randrange(0, int(pays_sheet1[-1:]['Upper Range']))
                        print(f"      Main Game Win: randomly chosen, for the wins: {random}")
                        for w, wrow in pays_sheet1.iterrows():
                           if(random >= wrow["Lower Range"] and random <= wrow["Upper Range"]):
                              print(f"         Winner! would add {wrow[0]} to the total, found between {wrow['Lower Range']} and {wrow['Upper Range']}")
         else:
            sn = i+1
            print(f"!!! Calling Bonus Game '{row[0]}' at row {sn} on the Trigger sheet !!!!!!!!!!!!!!!!!!!!!!!!!!!")
            # using i+1 because it counts up from zero programatically, and the sheets are referenced starting at 1.
            toPass = []
            #exec("print(f' Trying: spin_sheet = spin_sheet%d')" % sn)
            exec("toPass.append(spin_sheet%d)" % sn)
            #exec("print(f' Trying: lines_sheet = lines_sheet%d')" % sn)   
            exec("toPass.append(lines_sheet%d)" % sn)
            #exec("print(f' Trying: pays_sheet = pays_sheet%d')" % sn)
            exec("toPass.append(pays_sheet%d)" % sn)
            bonus_game(toPass[0], toPass[1], toPass[2])

#for i in liststuff:
#    exec("var%d = %d" % (i, i) )  ## (globals, locals)

for i in range(0, 40):
   play_game()