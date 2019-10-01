import json
from pathlib import Path

f = open("../json/2020_database_temp.json")
data = json.load(f)
f.close()

gw_input = 2
import operator

def calculate_overall_league_position():
    table_list = []

    # create a sortable list
    for player in data:
        player_list = []

        player_list.insert(0, player.title())                         #0 - player name
        player_list.insert(1, data[player]["team name"])              #1 - team name
        player_list.insert(2, data[player]["overall points"])         #2 - overall points
        player_list.insert(3, data[player]["total league points"])    #3 - league points

        table_list.append(player_list)

    #sort the list
    table_list = sorted(table_list, key = lambda x: (x[3]*-1, x[2]*-1, x[1]))
    
    #cycle through sorted list and define league position
    #including if there are equally positioned teams 
    #(i.e. same points and score)
    for idx,item in enumerate(table_list):
        
        prev_position = 0
        prev_score = 0
        prev_points = 0
        
        position = 0
        
        if idx == 0:
            position = idx + 1
            previous_position = idx + 1
            
        else:
            if previous_points == table_list[idx][3] and previous_score == table_list[idx][2]:
                position = previous_position
            else:
                position = idx + 1
                previous_position = idx + 1
                
        previous_score = table_list[idx][2]
        previous_points = table_list[idx][3]
        
        print("#" + str(position), table_list[idx][1], table_list[idx][2], table_list[idx][3])
        
calculate_overall_league_position()
