#minimal_excellerator.py

import sys
import os
import os.path
import math
import random
import numpy as np        # rounding
import pandas as pd

class Minimal_Excellerator():
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

        self.paylines = 50   # just setting this, because it used to be calculated in the old script. 
        self.this_bet = bet * self.paylines

        #paytable and bonus setup
        self.wintable = []
        self.read_wintable()  # table to see if you won, and how many spins
        self.paytable = []
        self.read_paytable()  # table for payouts, the 'wins'
        self.freespintable = []
        self.fswintable = []
        self.fspaytable = []
        self.read_bonus() 

    # Build the win table, the table to see if you won
    def read_wintable(self):
        self.wintable = pd.read_excel(self.input_filepath, sheet_name=self.wintable_sheetname, usecols=self.columns)
        self.wintable.columns = self.wintable.columns.str.strip() # remove whitespace from beginning and end

    def read_paytable(self):
        self.paytable = pd.read_excel(self.input_filepath, sheet_name=self.paytable_sheetname, usecols=self.columns)
        self.paytable.columns = self.paytable.columns.str.strip() # remove whitespace from beginning and end
   
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
        self.adjust_credits(self.this_bet * -1)
        rand = random.randint(0, int(self.wintable[-1:]['Upper Range']) )
        # for each row in paytable, check to see if it's in range, if so Win! if bonus, then do bonus stuff. 
        for idx, row in self.wintable.iterrows():
            if(rand >= int(row["Lower Range"]) and rand <= int(row['Upper Range'])):
                # if it's a bonus game, or extra spins: do that.
                if( (row['Win Lines'] == "Bonus Game") or (row['Win Lines'] == "Free Spins") ):
                    self.bonus_game()
                else:
                    if(row['Win Lines'] > 0):
                        self.payout(row['Win Lines'])
                break

    def bonus_game(self):
        """This is where the bonus games happen"""
        freespins = 0
        winlines = 0
        self.round_win = 0
        rand = random.randint(0, int(self.freespintable[-1:]['Upper Range']) )
        for idx, row in self.freespintable.iterrows():
            if(rand >= int(row["Lower Range"]) and rand <= int(row['Upper Range'])):             
                freespins = row['Free Spins']
                break

        for i in range(0,freespins):
            #decide how many winlines this spin
            rand = random.randint(0, int(self.fswintable[-1:]['Upper Range']) )
            for idx, row in self.fswintable.iterrows():
                if(rand >= int(row["Lower Range"]) and rand <= int(row['Upper Range'])):
                    winlines = row['Bonus Win Lines']
            this_spin_win = 0
            for j in range(0,winlines):
                self.this_win = 0
                rand = random.randint(0, int(self.fspaytable[-1:]['Upper Range']) )
                for idx, row in self.fspaytable.iterrows():
                    if(rand >= int(row["Lower Range"]) and rand <= int(row['Upper Range'])):
                        self.this_win += row['Bonus Pay Amount'] * self.bet_per_line
                        self.round_win += self.this_win
                        self.win_toggle = 1
                        this_spin_win += self.this_win

        if(self.win_toggle == 1):
            self.adjust_credits( self.round_win )
            self.round_win  = 0
            self.win_toggle = 0

    def payout(self, lines):
        """pays out *lines* number of win amounts from the Pay Values table"""
        self.round_win = 0
        for i in range(0, lines):
            rand = random.randint(0, int(self.paytable[-1:]['Upper Range']) )
            for idx, row in self.paytable.iterrows():
                if(rand >= int(row["Lower Range"]) and rand <= int(row['Upper Range'])):
                    self.this_win = row['Pay Amount'] * self.bet_per_line 
                    self.round_win += self.this_win
                    self.win_toggle = 1
        if(self.win_toggle == 1):
            self.adjust_credits(self.round_win)
            self.win_toggle = 0    

    def adjust_credits(self,value):
        # bets should be negative values, wins or deposits positive
        #adjust credits, set to 2 decimal pplaces, this should rounds appropriately in all situations. 
        self.game_credits = np.round(float(self.game_credits) + value, 2)
        if(self.debug_level >= 1):
            print(f"    $$$$ Adjusted credits by {str(value)}, now game wallet at: {str(self.game_credits)}")

    def return_credits(self):
         return self.game_credits            

#end class Excellerator