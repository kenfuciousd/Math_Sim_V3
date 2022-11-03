from collections import defaultdict
from datetime import datetime
import pandas as pd     # for reading Excel
import matplotlib.pyplot as plt  # for displaying math


class Minimal_Simulator():
    """ simulator class: takes in the SlotMachine class object, does stuff and tracks it. """
    def __init__(self, sm, simnum, debug_level):
        self.simnum = simnum
        self.sm = sm
        self.this_bet = sm.bet_per_line * float(sm.paylines)
        self.spins = []
        self.win_list = []        
        self.debug_level = debug_level
        self.total_bet = 0
        self.total_won = 0
        self.plot_toggle = 0 
        self.tenthousands = 0
        self.run_sim()
        #self.plot_result()   # the automatic plotting was causing issues with things hanging until it closed. 

    def run_sim(self):
        """This is really where it begins, once the simulation has been set up. so once the simulator has been
           initialized, it just starts running. This is the main area where time and math keeping happen x"""
        print(f"Beginning Simulation.")
        last = datetime.now()
        for iteration in range(self.simnum):
            if( iteration%10000 == 0 ):
                self.tenthousands += 1
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S")
                print(f"Generated {self.tenthousands}0000 records, at {current_time}.  It has been {now-last} since the last message.")
                last = now
            if( self.this_bet > float(self.sm.game_credits) ):
                if(self.sm.infinite_checked == True):
                    self.sm.game_credits += float(self.sm.initial_credits)
                else:    
                    print("!!!! Not enough credits, $" + str(self.this_bet) + " is required.")
                    break
            self.sm.play_game()
            self.spins.append(iteration + 1)
            self.win_list.append(int(round(self.sm.round_win * 100)))