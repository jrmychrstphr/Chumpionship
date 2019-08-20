import json
from pathlib import Path

f = open("../json/2020_database_temp.json")
data = json.load(f)
f.close()

gw_input = 1

for player in data:
    
    team_name  = data[player]["team name"]
    overall_points  = data[player]["overall points"]
    league_points  = data[player]["total league points"]
    
    print(team_name, league_points, overall_points)