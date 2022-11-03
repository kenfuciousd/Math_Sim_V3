#scratchpad.py

import pandas as pd
import random
from datetime import datetime
import time

now = datetime.now()

current_time = now.strftime("%H:%M:%S")
print(f"Dateless current time = {current_time}")

start_time = time.time()

time.sleep(3)

end_time = time.time()

run_time = end_time - start_time

print(f"total time run was {run_time}, with start being {start_time}")