from collections import defaultdict
from datetime import datetime
import pandas as pd     # for reading Excel
import matplotlib.pyplot as plt  # for displaying math


class Simulator():
    """ simulator class: takes in the SlotMachine class object, does stuff and tracks it. """
    def __init__(self, sm, simnum, debug_level):
        self.simnum = simnum
        self.sm = sm
        self.this_bet = sm.bet_per_line * float(sm.paylines)
        self.incremental_credits = []
        self.incremental_rtp = []
        self.spins = []
        self.win_list = []  # takes up the header line and lets us start at iteration 1 for data purposes
        self.rtp_dict = ["RTP"] # takes up the header line and lets us start at iteration 1 for data purposes
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
                # can't really send back a status to the gui?? 
                #simgui.slot_check.set("[Reset Slot]")
                if(self.debug_level >= 2):
                    print(f"    $$$$ no futher credits, if this is true: {self.sm.infinite_checked} then we should see credits added and spins continue")
                if(self.sm.infinite_checked == True):
                    self.sm.game_credits += float(self.sm.initial_credits)
                    if(self.debug_level >= 1):
                        print(f"    $$$$ adding {self.sm.initial_credits}, credits should now reflect that at: {self.sm.game_credits} ")
                #if it's not infinite credits mode, then this ends the simulation. 
                else:    
                    print("!!!! Not enough credits, $" + str(self.this_bet) + " is required.")
                    break
        #main game loop 
            # some of the busy parts of the simulator. spin the slotmachine(sm)'s reels and track the data
            # choosing a list for the win_list var because it's easy to convert to a DataFrame later. 
            #self.total_bet += self.this_bet 
            if(self.debug_level >= 1):
                print(f"spin {str(iteration+1)} and credits ${str(self.sm.return_credits())}")
            #self.sm.spin_reels()
            self.sm.play_game()
            #self.total_won += self.sm.round_win 
            self.incremental_rtp.append( (self.sm.total_won / self.sm.total_bet) * 100 )
            self.incremental_credits.append(self.sm.return_credits())
            self.spins.append(iteration + 1)
            # load the rtp from this round
            self.rtp_dict.insert(iteration + 1, (self.sm.total_won / self.sm.total_bet))
            # load the win from this round
            self.win_list.append(int(round(self.sm.round_win * 100)))
            if(self.debug_level >= 1):
                print(f"    .... win_list is {len(self.win_list)} long and it should add {round(self.sm.round_win * 100)}, at spin {self.spins[-1]}")
                if(len(self.win_list) != self.spins[-1]):
                    print(f"IT BROKE HERE")
            if(self.debug_level >= 3):
                print(f"    spin {str(iteration)} and credits ${str(self.sm.return_credits())} and added to the dictionary: {self.win_list[iteration]}")


    def plot_credits_result(self):
        #plt.style.use('_mpl-gallery')
        if(self.plot_toggle == 0):
            #plt.clf()
            self.plot_toggle = 2
        if(self.plot_toggle == 1):
            plt.clf()
            self.plot_toggle = 2
        plt.ylabel('Credits')
        plt.xlabel('Spins')
        plt.xlim(-1,self.simnum) # show total expected spins. 
        plt.ylim(-1,(max(self.incremental_credits))*1.2)
        plt.plot(self.spins, self.incremental_credits)
        plt.show()

    def plot_rtp_result(self):
        rtp = []
        if(self.plot_toggle == 0):
            #plt.clf()
            self.plot_toggle = 1
        if(self.plot_toggle == 2):
            plt.clf()
            self.plot_toggle = 1
        plt.ylabel('Return To Player %')
        plt.xlabel('Spins')
        plt.xlim(-1,self.simnum) # show total expected spins.
        plt.ylim(-1,(max(self.incremental_rtp)*1.2)) 
        plt.plot(self.spins, self.incremental_rtp)
        #print(f'debug plot: rtp is {self.sm.rtp}')
        for i in range(0, len(self.spins)):
            rtp.append(self.sm.rtp)
        plt.plot(self.spins, rtp, linestyle = 'dashed', color='magenta')
        # the multipliers create invariance in display 
        plt.text(self.spins[len(self.spins)-1] * 0.68, self.sm.rtp * 1.05, "Expected RTP " + str(round(rtp[0], 2)) + "%", color='magenta')
        plt.show()       

    # this should be used, in some form.. I don't like addressing this directly. However 
    #def return_dataframe(self):
    #    print(f" ... looking at {str(self.win_dict)}")
    #    return pd.DataFrame(self.win_dict)
