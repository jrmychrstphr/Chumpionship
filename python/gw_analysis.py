import json

#dowload the database
f = open("../json/2020_database.json")
data = json.load(f)
f.close()

#define gameweek
gw_input = 1

print('Enter gameweek:')
gw_input = int(input())


#create a list of player names and team names
player_list = []
for player in data:
    player_list.append(player)
    
# PRINT RECENT FORM

form_duration = 5   #define how many weeks back to show

#cycle through each player
for player in player_list:
    print("- - - - -")    
    print(player.title())    
    for x in range(gw_input-form_duration, gw_input):
        x += 1
        if x > 0:
            print("GW", x, ": ", data[player]["gw data"][str(x)]["fixture result"], data[player]["gw data"][str(x)]["fixture total"])