import json
from pathlib import Path

f = open("../json/2020_database.json")
data = json.load(f)
f.close()

gw_input = 2

#require user input to set gameweek
print('Enter gameweek to download:')
gw_input = int(input())

score_count = 0

gw_scores = []

for player in data:
    
    gw_scores.append(data[player]["gw data"][str(gw_input)]["fixture total"])
    
    
                    
print("Total: ", sum(gw_scores))
print("Avg: ", sum(gw_scores) / len(gw_scores))