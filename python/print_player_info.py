import json
from pathlib import Path

f = open("../json/2020_database_temp.json")
data = json.load(f)
f.close()

gw_input = 2

score_count = 0

for player in data:
    
    team_name  = data[player]["team name"]
    overall_points  = data[player]["overall points"]
    league_points  = data[player]["total league points"]
    gw_transfers  = data[player]["gw data"][str(gw_input)]["transfers made"]
    gw_spend  = data[player]["gw data"][str(gw_input)]["points spent"]
    
    score_count += data[player]["gw data"][str(gw_input)]["fixture total"]
    
    print(player, team_name)
    print("league_points", league_points)
    print("overall_points", overall_points)
    print("gw_transfers", gw_transfers)
    print("gw_spend", gw_spend)
    print(" ")
    
print("points scored: ", score_count)
print("average: ", score_count/20)