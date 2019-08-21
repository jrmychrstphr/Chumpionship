import json
from pathlib import Path

f = open("../json/2020_database_temp.json")
data = json.load(f)
f.close()

gw_input = 2

import operator

table_list = []

for player in data:
    player_list = []
    
    player_list.append(player.title())                            #0 - player name
    player_list.append(data[player]["team name"])               #1 - team name
    player_list.append(data[player]["overall points"])          #2 - overall points
    player_list.append(data[player]["total league points"])     #3 - league points
    
    
    #print(player_list)
    #print(" ")
    table_list.append(player_list)


#print(table_list)
#print(" ")

table_list = sorted(table_list, key = lambda x: (x[3]*-1, x[2]*-1, x[1]))

for idx,item in enumerate(table_list):
    table_list[idx].append(idx+1)                          #4 - position

#print(table_list)

previous_position = 0
previous_score = 0
previous_points = 0

for idx,player in enumerate(table_list):
    
    #print(idx, table_list[idx][0])
    
    if idx == 0:
        previous_position = table_list[idx][4]
        previous_score = table_list[idx][2]
        previous_points = table_list[idx][3]
    else:
        
        #print("previous_points", previous_points)
        #print("table_list[idx][3]", table_list[idx][3])
        #print(" ")
        #print("previous_score", previous_score)
        #print("table_list[idx][2]", table_list[idx][2])
        
        if previous_points == table_list[idx][3] and previous_score == table_list[idx][2]:
            #print("same")
            #print(table_list[idx][4])
            table_list[idx][4] = previous_position
            #print(table_list[idx][4])
            
        previous_position = table_list[idx][4]
        previous_score = table_list[idx][2]
        previous_points = table_list[idx][3]
            
print(table_list)

for idx,player in enumerate(table_list):
    data[table_list[idx][0].lower()]["league position"] = table_list[idx][4]

    
    
with open("../json/2020_database_temp.json", 'w') as outfile:
        print("Exporting data to temp file...")
        json.dump(data, outfile, sort_keys=True, indent=4, separators=(',', ': '))
        
# TO DO:
# - Make this iterative over multiple GWs
# - itergrate in to gw data update script
