import json

# Set up gw data items in database, for each gw add:
# - opponent name (player name)
# - points scored
# - points spent
# - fixture total
# - fixture result
# - chip played
# - squad

x = {}
x["opponent"] = ""
x["points scored"] = 0.0
x["points spent"] = 0.0
x["fixture total"] = 0.0
x["fixture result"] = ""
x["chip played"] = ""
x["squad"] = {}

# Load 2020 database


f = open("../json/2020_database.json")
data = json.load(f)
f.close()

print(data)

for player in data:
        print(player)
        
        for i in range(1, 39):
            data[player]["gw data"][i] = x

with open("../json/2020_database_temp.json", 'w') as outfile:
    json.dump(data, outfile, sort_keys=True, indent=4, separators=(',', ': '))