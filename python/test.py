import json
from pathlib import Path

f = open("../json/2020_database_temp.json")
data = json.load(f)
f.close()

gw_input = 1

for x in range(1, gw_input+1):
    print(x)