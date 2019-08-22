import json


f = open("../json/2020_database.json")
data = json.load(f)
f.close()

#define gameweek
gw_input = 1

print('Enter gameweek:')
gw_input = int(input())



#create a list of player names and team names
player_names_list = []
team_names_list = []
for player in data:
    player_names_list.append(player)
    team_names_list.append(data[player]["team name"])

#create a dictionary of fixtures
fixtures_list = []

while len(player_names_list) > 0:
    
    player_one_name = player_names_list.pop()
    player_two_name = data[player_one_name]["gw data"][str(gw_input)]["opponent"].lower()
    
    player_names_list.pop(player_names_list.index(player_two_name))
    
    player_one_team = data[player_one_name]["team name"]
    player_two_team = data[player_two_name]["team name"]
    
    fixture = {}
    
    fixture["player_one_team"] = player_one_team
    fixture["player_two_team"] = player_two_team
    
    fixtures_list.append(fixture)
    

print(fixtures_list)

#caluclate length of longest team name
team_name_lengths_list = []
for name in team_names_list:
    team_name_lengths_list.append(len(name))
    
max_name_length = max(team_name_lengths_list)
print(max_name_length)

#convert gw number to two digits
gw_code = "{0:0=2d}".format(gw_input)

#write the file
f= open("../plain_text_assets/"+gw_code+"---fixtures.txt","w+")

f.write("Chumpionship 2020\r\n \r\nGW" + str(gw_input) + " fixtures:\r\n \r\n")

for fixture in fixtures_list:
    
    #space out player one team name
    player_one_team = fixture["player_one_team"]
    
    if len(player_one_team) < max_name_length:
        spaces_needed = max_name_length - len(str(player_one_team))
        spaces = ''
        spaces += ' ' * spaces_needed
        
        player_one_team = player_one_team + spaces
            
    #space out player two team name
    player_two_team = fixture["player_two_team"]
    
    if len(player_two_team) < max_name_length:
        spaces_needed = max_name_length - len(str(player_two_team))
        spaces = ''
        spaces += ' ' * spaces_needed
        
        player_two_team = spaces + player_two_team

            
    f.write(player_one_team + "  vs  " + player_two_team + "\r\n")

        
f.close() 