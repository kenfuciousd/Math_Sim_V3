#Excellerator.py - replaces SlotMachine.py in the workflow, 

import sys
import os
import os.path
import math
import random
import numpy as np        # rounding
import pandas as pd

class Excellerator():
    """Excellerator class, takes in a number of gui elements: filepath, bet, initial credits, debug level, and infinite cash check box boolean """ 
    # initialize, setting allowances to settings:
    def __init__(self, filepath, bet, initial_credits, debug_level, infinite_checked):
        # initialization values 
        self.input_filepath = filepath
        self.game_credits = initial_credits   # the 'wallet' value 
        self.initial_credits = initial_credits  #specifically to save the value for the infinite check
        self.bet_per_line = bet
        self.infinite_checked = infinite_checked
        self.debug_level = debug_level

        # The Excel Sheet definition section
        self.wintable_sheetname = 'Win Lines'
        self.paytable_sheetname = 'Pay Values'
        self.freespin_sheetname = 'FG Spin Total'
        self.fswinlines_sheetname = 'FG Win Lines' # the sheet to see if they won
        self.fspaylines_sheetname = 'FG Pay Values'
        # this section is to define where we get our theoretical/pre-calculated values from.. 
        self.rtp_sheetname = 'Win Lines'   # it doesn't like 'Ways/Pays' in excel
        self.vi_sheetname = 'RTP'
        self.rtp_column = 'Total RTP'
        self.vi_column = 'Volatility'
        #self.columns = ['Win Lines', 'Weight', 'Lower Range', 'Upper Range']
        self.columns="A:D"  # the above column names.

        #self.paylines_total = 9 # 3x3 defaul0t value to be set later... in the paylines
        # the math section.
        self.paylines = 50   # just setting this, because it used to be calculated in the old script. 
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

        #paytable and bonus setup
        self.wintable = []
        self.read_wintable()  # table to see if you won, and how many spins
        self.paytable = []
        self.read_paytable()  # table for payouts, the 'wins'
        self.freespintable = []
        self.fswintable = []
        self.fspaytable = []
        self.read_bonus()
        # ## remaining initialization actions: 

        # debug announcement; the place for initial conditions to get checked or set.
        if(self.debug_level >= 1):
            print(f"DEBUG LEVEL 1 - basic math and reel matching info")
        if(self.debug_level >= 2):
            print(f"DEBUG LEVEL 2 - most debugging information, descriptive")
            print(f"        >>> the local variable {self.input_filepath} .. was saved from input {filepath}")
        if(self.debug_level >= 3):
            print(f"DEBUG LEVEL 3 - every other status message used for debugging - verbose, keep below ")


    # Build the win table, the table to see if you won
    def read_wintable(self):
        self.wintable = pd.read_excel(self.input_filepath, sheet_name=self.wintable_sheetname, usecols=self.columns)
        self.wintable.columns = self.wintable.columns.str.strip() # remove whitespace from beginning and end

        # ### string for testing this in command lines:
        # import pandas as pd
        # paytable_data = pd.read_excel('./assets/GameFitStrategy.xlsx', sheet_name='Win Lines', usecols="A:D")
        # 
        #self.paytable_data = pd.read_excel(self.input_filepath, sheet_name=self.paytable_sheetname, usecols=self.columns)
        #self.paytable = []
        #for idx, row in self.paytable_data.iterrows():
            # for each row
            #     print(f" {idx} .. {row} .. !! ")
        #    temprow = [] 
        #    for i in range(0, self.mod_paytable_data.shape[1]):
        #        temprow.append(row[i])
        #    self.paytable.append(temprow)

        if(self.debug_level >= 2):
            print(f"        Wintable: {self.wintable}")
        ### set the RTP

        #self.vi_data = pd.read_excel(self.input_filepath, sheet_name=self.vi_sheetname)
        ### this is where the data is pulled from the columns on the rtp sheetrtpself.rtp = self.rtp_data[self.rtp_column][0] * 100 ## times 100 so that we have the percentage that matches the data
        #self.vi = self.vi_data[self.vi_column][0]

    def read_paytable(self):
        self.paytable = pd.read_excel(self.input_filepath, sheet_name=self.paytable_sheetname, usecols=self.columns)
        self.paytable.columns = self.paytable.columns.str.strip() # remove whitespace from beginning and end
        self.mean_pay = 0
        for idx, line in self.paytable.iterrows():
            #print(f"line {line[len(line)-1]}")
            self.mean_pay += line['Pay Amount']
        self.mean_pay = self.mean_pay / len(self.paytable)
        if(self.debug_level >= 2):
            print(f"        $!MATH$! Paytable Mean Pay is {self.mean_pay}")        

    def read_bonus(self):
        self.freespintable = pd.read_excel(self.input_filepath, sheet_name=self.freespin_sheetname, usecols=self.columns)
        self.freespintable.columns = self.freespintable.columns.str.strip() # remove whitespace from beginning and end        
        self.fswintable = pd.read_excel(self.input_filepath, sheet_name=self.fswinlines_sheetname, usecols=self.columns)
        self.fswintable.columns = self.fswintable.columns.str.strip() # remove whitespace from beginning and end     
        self.fspaytable = pd.read_excel(self.input_filepath, sheet_name=self.fspaylines_sheetname, usecols=self.columns)
        self.fspaytable.columns = self.fspaytable.columns.str.strip() # remove whitespace from beginning and end     

    def play_game(self):
        # assumes error checking has happened, and now we play!
        self.this_win = 0
        self.round_win = 0

        if(self.debug_level >= 1):
            print(f"    -- betting {self.this_bet}")
        self.adjust_credits(self.this_bet * -1)
        #this_bet = self.bet_per_line * float(self.paylines_total)
        if(self.debug_level >= 3):
            print(f"            checking credits: {self.game_credits}  <  {str(this_bet)}")

        rand = random.randint(0, int(self.wintable[-1:]['Upper Range']) )
        if(self.debug_level >= 1):
            print(f"    ! Chose: {rand} against the win table")
        #once chosen, run through the paytable to see where it lands.
        # for each row in paytable, check to see if it's in range, if so Win! if bonus, then do bonus stuff. 
        for idx, row in self.wintable.iterrows():
            #print(f"rand: {rand} .. row {idx}; Weight {row['Weight']}; Win Lines: {row['Win Lines']} -- found:\n{str(row)}")
            #print(f"lower: {row['Lower Range']}; upper: {row['Upper Range']}")
            if(rand >= int(row["Lower Range"]) and rand <= int(row['Upper Range'])):
                if(self.debug_level >= 2):
                    print(f"        Hit! {rand} at row {idx} found between {row['Lower Range']} and {row['Upper Range']}")
                #print(f" -- we would award {row['Win Lines']}")

                # if it's a bonus game, or extra spins: do that.
                if( (row['Win Lines'] == "Bonus Game") or (row['Win Lines'] == "Free Spins") ):
                    #print(f"FOUND BONUS")
                    self.bonus_game()
                    # else adjust credits by row: 'win lines'
                else:
                    if(row['Win Lines'] > 0):
                        if(self.debug_level >= 1):
                            print(f"    ++ Win, now running {row['Win Lines']} times against the win line table")
                        # payout has the payout logic, with win amounts    
                        self.payout(row['Win Lines'])
                break
                
            else: 
                if(self.debug_level >= 2):
                    print(f"        -- Miss! {rand} at row {idx}, not between {row['Lower Range']} and {row['Upper Range']}")

    def bonus_game(self):
        """This is where the bonus games happen"""

        if(self.debug_level >= 1):
            print(f"    -> RUNNING BONUS GAME <- ")
        freespins = 0
        winlines = 0
        self.round_win = 0

        # decide how many spins
        rand = random.randint(0, int(self.freespintable[-1:]['Upper Range']) )
        if(self.debug_level >= 1):
            print(f"    ## Chose random number: {rand} for Free Spins Number Table ")
        for idx, row in self.freespintable.iterrows():
            if(self.debug_level >= 2):
                print(f"           ???? checking {idx}, is {rand} between {row['Lower Range']} and {row['Upper Range']}?  ")
            # currently wrong. 
            if(rand >= int(row["Lower Range"]) and rand <= int(row['Upper Range'])):
                if(self.debug_level >= 1):
                    print(f"      #### Set to be playing {row['Free Spins']} Free Games.")                
                freespins = row['Free Spins']
                break
        # run the free spins        
        for i in range(0,freespins):
            #decide how many winlines this spin
            rand = random.randint(0, int(self.fswintable[-1:]['Upper Range']) )
            if(self.debug_level >= 1):
                print(f"        #### For Free Spin {i+1}, chose {rand} for Free Spins on the FreeGame Pay Values Table")
            for idx, row in self.fswintable.iterrows():
                if(rand >= int(row["Lower Range"]) and rand <= int(row['Upper Range'])):
                    if(self.debug_level >= 1):
                        print(f"          ## and that means {row['Bonus Win Lines']} lines won on the Bonus Win Lines Table")
                    winlines = row['Bonus Win Lines']
            this_spin_win = 0
            # for each of those winlines, run it against the Free Game Pay Values 
            for j in range(0,winlines):
                self.this_win = 0
                rand = random.randint(0, int(self.fspaytable[-1:]['Upper Range']) )
                if(self.debug_level >= 2):
                    print(f"            $$ On BONUS WIN Table: Bonus Game Line {j+1}, Chose value {rand} for Bonus Win ")
                for idx, row in self.fspaytable.iterrows():
                    if(rand >= int(row["Lower Range"]) and rand <= int(row['Upper Range'])):
                        self.this_win += row['Bonus Pay Amount'] * self.bet_per_line
                        self.round_win += self.this_win
                        self.win_toggle = 1
                        this_spin_win += self.this_win
                        if(self.debug_level >= 2):
                            print(f"                $$$$$$$$ Bonus Round, {rand} result pays out at {row['Bonus Pay Amount']} credits, paying ${self.this_win}")
            if(self.debug_level >= 1):
                print(f"                    $$$$$$$$ Bonus Round: Freespin {i+1}, this round {this_spin_win} total payout up to: {self.round_win}")
        # Then, if it was a win, do the math 
        if(self.win_toggle == 1):
            self.adjust_credits( self.round_win )
            self.round_win  = 0
            self.hit_total += 1
            self.bonus_hit_count += 1
            self.win_toggle = 0
            if(self.round_win > self.maximum_liability):
                self.maximum_liability = self.round_win
            self.summation += (self.mean_pay - self.round_win ) ** 2
            if(self.debug_level >= 2):
                print(f"    +=+=+=+= summation is now {self.summation}, which added: ({self.mean_pay} minus {self.round_win}) squared. ")
            #### keeping, but from prior value from SlotMachine.py
            #self.summation += (self.mean_pay - (win_combo[len(win_combo)-1] ) ) ** 2
            #total_win_display = "{:.2f}".format(total_win) 

    def payout(self, lines):
        """pays out *lines* number of win amounts from the Pay Values table"""
        self.round_win = 0
        for i in range(0, lines):
            rand = random.randint(0, int(self.paytable[-1:]['Upper Range']) )
            if(self.debug_level >= 2):
                print(f"    #### In Payout, Randomly chosen: {rand}")
            #once chosen, run through the paytable to see where it lands.
            # for each row in paytable, check to see if it's in range, if so Win! if bonus, then do bonus stuff. 
            for idx, row in self.paytable.iterrows():
                #print(f"rand: {rand} .. row {idx}; Weight {row['Weight']}; Win Lines: {row['Win Lines']} -- found:\n{str(row)}")
                #print(f"lower: {row['Lower Range']}; upper: {row['Upper Range']}")
                if(rand >= int(row["Lower Range"]) and rand <= int(row['Upper Range'])):
                    #self.this_win += row['Pay Amount']
                    if(self.debug_level >= 1):
                        print(f"    $$$$ Iteration {i+1}: win by {row['Pay Amount'] * self.bet_per_line}, adding to this round's win")
                    self.this_win = row['Pay Amount'] * self.bet_per_line 
                    self.round_win += self.this_win
                    self.win_toggle = 1
        if(self.debug_level >= 2):
            print(f"        $$$$ ++++ TOTAL win this round: {self.round_win}, with a total simulator win of {self.total_won}")
        # Then, if it was a win, do the math
        if(self.win_toggle == 1):
            self.adjust_credits(self.round_win)
            self.hit_total += 1
            self.win_toggle = 0    
            if(self.round_win > self.maximum_liability):
                self.maximum_liability = self.round_win
            self.summation += (self.mean_pay - self.round_win ) ** 2
            if(self.debug_level >= 2):
                print(f"    +=+=+=+= summation is now {self.summation}, which added: ({self.mean_pay} minus {self.round_win}) squared. ")

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

#end class Excellerator