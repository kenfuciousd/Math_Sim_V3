#Excellerator2.py

import sys
import os
import os.path
import math
import random as rd
import numpy as np        # rounding
import pandas as pd

class Excellerator2():
    def __init__(self, filepath, bet, initial_credits, debug_level, infinite_checked):
        # initialization values 
        self.input_filepath = filepath
        self.game_credits = initial_credits   # the 'wallet' value 
        self.initial_credits = initial_credits  #specifically to save the value for the infinite check
        self.bet_per_line = bet
        self.infinite_checked = infinite_checked
        self.debug_level = debug_level
        self.settings_sheetname = 'Settings"'
        self.excel_file = pd.ExcelFile(self.input_filepath)
        self.eset_df = excel_file.parse(self.settings_sheetname, index_col = 0)
        if(self.debug_level >= 3):
            for idx, item in eset_df.iterrows():
               print(f"index: '{idx}' and \n row '{item['value']}' .. \n")

        # this section is to define where we get our theoretical/pre-calculated values from.. 
        self.rtp_sheetname = 'Win Lines'   # it doesn't like 'Ways/Pays' in excel
        self.vi_sheetname = 'RTP'
        self.rtp_column = 'Total RTP'
        self.vi_column = 'Volatility'
        #self.columns = ['Win Lines', 'Weight', 'Lower Range', 'Upper Range']
        self.columns="A:D"  # the above column names.

        #self.paylines_total = 9 # 3x3 defaul0t value to be set later... in the paylines
        # the math section.
        self.paylines = 0   # just setting this, because it used to be calculated in the old script. 
        # ---- this will need to be calculated.
        self.winlines = 0
        self.hit_total = 0
        self.maximum_liability = 0
        #for volatility
        self.volitility = float(0)
        self.mean_pay = 0
        self.summation = 0
        #for betting
        self.this_bet = bet * self.paylines
        self.this_win = 0    # value to be returned for tracking
        self.round_win = 0
        self.total_won = 0
        self.total_bet = 0 
        #if(self.debug_level >= 2):
        #    print(f"        = Total bet is being set and is {self.total_bet}")
        self.rtp = 0
        self.vi = 0
        self.bonus_hit_count = 0
        # debug announcement; the place for initial conditions to get checked or set.
        if(self.debug_level >= 1):
            print(f"DEBUG LEVEL 1 - basic math and reel matching info")
        if(self.debug_level >= 2):
            print(f"DEBUG LEVEL 2 - most debugging information, descriptive")
            print(f"        >>> the local variable {self.input_filepath} .. was saved from input {filepath}")
        if(self.debug_level >= 3):
            print(f"DEBUG LEVEL 3 - every other status message used for debugging - verbose, keep below ")
        # LOAD - Access the excel file
        self.load_excel()        
        # for each set, table 1 would be #spins, table 2 is paylines, table 3 is win values

    def load_excel():
        """ takes in the excel file, and performs the setup logic""" 
        excel_file = pd.ExcelFile(self.input_filepath)
        sheet_count = 0
        self.spin_sheet1 = excel_file.parse(sheet_name=sheet_count, usecols=self.columns)
        self.spin_sheet1.columns = self.spin_sheet1.columns.str.strip()
        sheet_count += 1
        games_total = len(spin_sheet1)  # this is how many bonus games we have
        #print(f"found {games_total} total games!")
        self.lines_sheet1 = excel_file.parse(sheet_name=sheet_count, usecols=self.columns)
        self.lines_sheet1.columns = self.lines_sheet1.columns.str.strip()
        sheet_count += 1
        self.pays_sheet1 = excel_file.parse(sheet_name=sheet_count, usecols=self.columns)
        self.pays_sheet1.columns = self.pays_sheet1.columns.str.strip()
        self.mean_pay = 0
        for idx, line in self.pays_sheet1.iterrows():
            #print(f"line {line[len(line)-1]}")
            self.mean_pay += line[0]
        self.mean_pay = self.mean_pay / len(self.pays_sheet1)
        #### EXAMINE THIS - DOES BONUS ADD INTO THE MEAN AS WELL? MATTERS FOR LATER MATH
        if(self.debug_level >= 2):
            print(f"        $!MATH$! Paytable Mean Pay is {self.mean_pay}")        

        sheet_count += 1
        # now dynamically build the bonus games
        for i in range(2, games_total+1):
            print(f"Loading Bonus Game sheet {i} at sheet_count {sheet_count}")
            exec("self.spin_sheet%d = excel_file.parse(sheet_name=sheet_count, usecols=self.columns)" % i)
            exec("self.spin_sheet%d.columns = self.spin_sheet%d.columns.str.strip()" % (i, i))
            #print(f'SPIN SHEET {i}:')
            #exec("print(f'{spin_sheet%d}')" % i)
            sheet_count += 1
            exec("self.lines_sheet%d = excel_file.parse(sheet_name=sheet_count, usecols=self.columns)" % i)
            exec("self.lines_sheet%d.columns = self.lines_sheet%d.columns.str.strip()" % (i, i))
            #print(f"LINES SHEET {i}:")
            #exec("print(f'{lines_sheet%d}')" % i)
            sheet_count += 1
            exec("self.pays_sheet%d = excel_file.parse(sheet_name=sheet_count, usecols=self.columns)" % i)
            exec("self.pays_sheet%d.columns = self.pays_sheet%d.columns.str.strip()" % (i, i))
            #print(f"PAYS SHEET {i}:")
            #exec("print(f'{pays_sheet%d}')" % i)
            sheet_count += 1

    def adjust_credits(self,value):
        # bets should be negative values, wins or deposits positive
        # for totals tracked
        if(value >= 0):
            self.total_won += value
            if(self.debug_level >= 2):
                print(f"                     STATUS: total_won is: {self.total_won}")
        elif(value < 0):
            # negative to offset the negative value of the bet itself. 
            self.total_bet -= value
            if(self.debug_level >= 2):
                print(f"                     STATUS: total_bet is: {self.total_bet}")
        #adjust credits, set to 2 decimal pplaces, this should rounds appropriately in all situations. 
        self.game_credits = np.round(float(self.game_credits) + value, 2)
        if(self.debug_level >= 1):
            print(f"    $$$$ Adjusted credits by {str(value)}, now game wallet at: {str(self.game_credits)}")

    def return_credits(self):
        return self.game_credits 

    def bonus_game(self, spin_sheet, lines_sheet, pays_sheet):
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
                             
    def play_game(self):
       # The "Game Spins".. if this were a slot, it would be the "play game" button. Will use spin_sheet1, lines_sheet1, and pays_sheet1
        self.this_win = 0
        self.round_win = 0
        if(self.debug_level >= 1):
            print(f"    -- betting {self.this_bet}")
        self.adjust_credits(self.this_bet * -1)
        if(self.debug_level >= 3):
            print(f"            checking credits: {self.game_credits}  <  {str(this_bet)}")

       # random number vs spin table.   ## set upper range as a variable, so we don't have to keep calling the data structure? 
        random = rd.randrange(0, int(self.spin_sheet1[-1:]['Upper Range']))
        if(self.debug_level >= 1):
                print(f"Main Game Initial Bonus Trigger, randomly chosen, for the spin: {random}")
        for i, row in self.spin_sheet1.iterrows():
            if(random >= row["Lower Range"] and random <= row["Upper Range"]):
                if(self.debug_level >= 1):
                    print(f"   Found {random} is between {row['Lower Range']} and {row['Upper Range']}")
                if(i == 0):
                    if(self.debug_level >= 1):
                        print(f"Playing Main Game")
                    random = rd.randrange(0, int(self.lines_sheet1[-1:]['Upper Range']))
                    if(self.debug_level >= 1):
                        print(f"   Main Game Lines: randomly chosen, for the lines: {random}")
                    for l, lrow in self.lines_sheet1.iterrows():
                        if(random >= lrow["Lower Range"] and random <= lrow["Upper Range"]):
                            if(self.debug_level >= 1):
                                print(f"      Chose {lrow[0]} Line Wins")
                            if(lrow[0] > 0):
                                for lines in range(0, lrow[0]):  
                                    random = rd.randrange(0, int(self.pays_sheet1[-1:]['Upper Range']))
                                    if(self.debug_level >= 1):
                                        print(f"      Main Game Win: randomly chosen, for the wins: {random}")
                                    for w, wrow in self.pays_sheet1.iterrows():
                                        if(random >= wrow["Lower Range"] and random <= wrow["Upper Range"]):
                                            if(self.debug_level >= 1):
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
