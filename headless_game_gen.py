#!/opt/homebrew/bin/python3

#quick_game_gen.py
# meant to be run at command line, to build game simulation files more quickly. 

# dependencies
import pandas as pd
import numpy as np
#from classes.Excellerator import Excellerator
from classes.minimal_excellerator import Minimal_Excellerator
#from classes.Simulator import Simulator
from classes.minimal_simulator import Minimal_Simulator
import time
import os
import math


if __name__ == '__main__':
    # you probably want debug at zero, here, in order to generate things quickly. 
    debug_level = 0
    initial_credits = 1000
    machine_credits = 0
    #simruns = 50000 
    # defaulting at 10 million, change the simulation runs here.
    simruns = 10000000
    # this is where the input goes, if you want a different file.
    input_filepath = "./assets/GameFitStrategy.xlsx"
    sim_output_filepath = "./assets/simdata.csv"
    df = pd.DataFrame()
    # if you want a different bet, this is what you change. 
    bet = float('0.01')
    start_time = time.time()
    print(f"Beginning headless Simulation, generating {simruns} simulations, beginning at {start_time}")

    # excellerator class input is: filepath, bet, initial credits, debug level (leaving at 0), and the infinite-checked boolean. 
    #excellerator = Excellerator(input_filepath, bet, initial_credits, debug_level, True)
    excellerator = Minimal_Excellerator(input_filepath, bet, initial_credits, debug_level, True)

    # simulator class input is: excellerator instanced object, simnum, debug_level
    start_time = time.time()
    sim = Minimal_Simulator(excellerator, simruns, debug_level)   # simulator call 
    df = pd.DataFrame(sim.win_list)   #, columns=['Credits'])  # pull the saved simulator dat

    # Output the results
    print(f"    Sim Output Saving... to {sim_output_filepath}")
    if(os.path.exists(sim_output_filepath) == False):
        with open(sim_output_filepath, 'w') as fp:
            fp.close()
    df.to_csv(sim_output_filepath, index=False, header=False)
    print(f"Output saved")

    end_time = time.time()
    run_time = np.round(end_time - start_time, 2) 
    mrt = np.round(run_time / 60 ,2) 
    print(f"Simulation Complete, total run time in seconds: {run_time}, approximately {mrt} minutes, played {sim.spins[-1]} spins.")
