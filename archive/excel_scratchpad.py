#scratchpad.py

import pandas as pd
import random

input_filepath = "../assets/GameFitStrategy.xlsx"
# The Excel Sheet definition section
wintable_sheetname = 'Win Lines'
paytable_sheetname = 'Pay Values'
# this section is to define where we get our theoretical/pre-calculated values from.. 
rtp_sheetname = 'Win Lines'   # it doesn't like 'Ways/Pays' in excel
vi_sheetname = 'RTP'
rtp_column = 'Total RTP'
vi_column = 'Volatility'
#columns = ['Win Lines', 'Weight', 'Lower Range', 'Upper Range']
columns="A:D"  # the above column names.

# read and sanitize data
paytable = pd.read_excel(input_filepath, sheet_name=paytable_sheetname, usecols=columns)
paytable.columns = paytable.columns.str.strip() # remove whitespace from beginning and end

wintable = pd.read_excel(input_filepath, sheet_name=wintable_sheetname, usecols=columns)
wintable.columns = wintable.columns.str.strip() # remove whitespace from beginning and end

rand = random.randint(0, int(paytable[-1:]['Upper Range']) )
print(f"Randomly chosen: {rand}")
#once chosen, run through the paytable to see where it lands.
# for each row in paytable, check to see if it's in range, if so Win! if bonus, then do bonus stuff. 
for idx, row in paytable.iterrows():
    #print(f"rand: {rand} .. row {idx}; Weight {row['Weight']}; Win Lines: {row['Win Lines']} -- found:\n{str(row)}")
    #print(f"lower: {row['Lower Range']}; upper: {row['Upper Range']}")
    if(rand in range(int(row["Lower Range"]),int(row['Upper Range']))):
        print(f"Hit! {rand} at row {idx} found between {row['Lower Range']} and {row['Upper Range']}")
        print(f" -- we would award {row['Win Lines']} spins at the win table")
        #if reward is 'bonus game': Run bonus game, which  
        if( (row['Win Lines'] == "Bonus Game") or (row['Win Lines'] == "Free Spins") ):
            print(f"  BONUS  ")
        else: 
            print(f"run {row['Win Lines']} times against the win line table") 
        #elif 'free spins':
        # elif 'pick bonus': 
        #else: take win line # of spins at the win table
        break
    else: 
        print(f"Miss! {rand} at row {idx}, not between {row['Lower Range']} and {row['Upper Range']}")