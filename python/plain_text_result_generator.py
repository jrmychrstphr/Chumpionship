import json


f = open("../json/2020_database_temp.json")
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
    
    player_one_score = data[player_one_name]["gw data"][str(gw_input)]["fixture total"]
    player_two_score = data[player_two_name]["gw data"][str(gw_input)]["fixture total"]
    
    player_one_result = data[player_one_name]["gw data"][str(gw_input)]["fixture result"]
    player_two_result = data[player_two_name]["gw data"][str(gw_input)]["fixture result"]
    
    player_one_team = data[player_one_name]["team name"]
    player_two_team = data[player_two_name]["team name"]
    
    fixture = {}
    
    fixture["player_one_team"] = player_one_team
    fixture["player_two_team"] = player_two_team
    fixture["player_one_score"] = player_one_score
    fixture["player_two_score"] = player_two_score
    fixture["player_one_result"] = player_one_result
    fixture["player_two_result"] = player_two_result
    
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
f= open("../plain_text_assets/"+gw_code+"---results.txt","w+")

f.write("Chumpionship 2020\r\n \r\nGW" + str(gw_input) + " results:\r\n \r\n")

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
        
    #space out scores
    player_one_score = str(fixture["player_one_score"])
    player_two_score = str(fixture["player_two_score"])
    
    if len(player_one_score) < 3: 
        player_one_score = " " + player_one_score
    
    if len(player_two_score) < 3: 
        player_two_score = player_two_score + " "
        

    #determine result indicator
    player_one_result = str(fixture["player_one_result"])
    player_two_result = str(fixture["player_two_result"])
    
    if player_one_result == "win":
        player_one_result = "(*) "
    else:
        player_one_result = "    "
        
    if player_two_result == "win":
        player_two_result = " (*)"
    else:
        player_two_result = "    "
        
    
    

    score = "  " + player_one_score + " // " + player_two_score +   "  "
            
    f.write(player_one_result + player_one_team + score + player_two_team + player_two_result + "\r\n")
    
    
f.write("\r\n- - -\r\n(*) denotes fixture winners")
        
f.close() 