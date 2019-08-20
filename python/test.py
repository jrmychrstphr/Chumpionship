import json
from pathlib import Path

f = open("../json/2020_database_temp.json")
data = json.load(f)
f.close()

gw_input = 2

for player in data:
    print("")
    print(player)
    
    score_count = 0
    transfers_count = 0
    spend_count = 0
    league_points_count = 0
    
    for x in range(1, gw_input+1):
        score_count = score_count + data[player]["gw data"][str(x)]["points scored"]
        transfers_count = transfers_count + data[player]["gw data"][str(x)]["transfers made"]
        spend_count = spend_count + data[player]["gw data"][str(x)]["points spent"]

        fixture_result = data[player]["gw data"][str(x)]["fixture result"]

        if fixture_result == "win":
            league_points_count = league_points_count + 3
        elif fixture_result == "draw":
            league_points_count = league_points_count + 1
        elif fixture_result == "loss":
            league_points_count = league_points_count + 0
        else:
            print("Error in calculating league points gained in gw", x)

    data[player]["total points scored"] = score_count
    data[player]["total points spent"] = spend_count
    data[player]["overall points"] = score_count - spend_count
    data[player]["total league points"] = league_points_count
    data[player]["total transfers made"] = transfers_count

    print("total transfers made:", transfers_count)

    print("total points scored:", score_count)
    print("total points spent:", spend_count)
    print("overall score:", score_count - spend_count)

    print("total league points:", league_points_count)