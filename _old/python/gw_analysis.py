# Gameweek analysis
# - Scoreboard (GW)
# - Scoreboard (Overall total)*
# - GW scores (Ranks, top 10)*
# - GW scores (Ranks, bottom 10)
# - Result streaks (Current, Previous) i.e. W1 (L5) = First win after a run of 5 losses
# - Winning runs (Current)
# - Winning runs (Overall ranks)
# - Winless runs (Current)
# - Winless runs (Overall ranks)
# - GW Match-ups (Highest combined score)
# - GW Match-ups (Lowest combined score)
# - GW Match-ups (Biggest margin)
# - Chips used (GW Summary)


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
    

## Scoreboards ##

def create_scoreboards():
    
    #create a list of dictionaries of all scores
    list_of_scores = []
    
    for player in data:
        
        team_name = data[player]["team name"]
        first_name = data[player]["first name"]
        surname = data[player]["surname"]
        player_name = first_name + " " + surname
        
        for gw in range (1, gw_input+1):
            
            score_dict = {}
            
            score_dict["gw"] = gw
            score_dict["fixture total"] = data[player]["gw data"][str(gw)]["fixture total"]
            score_dict["player name"] = player_name
            score_dict["team name"] = team_name
            
            list_of_scores.append(score_dict)
            
    sorted_list_of_scores = sorted(list_of_scores, key=lambda k: k["fixture total"], reverse=True)
    
    ## Scorebord printer function ##
    
    def print_scoreboard(table_data):
        
        rank = 0    # define rank variable
        prev_score = 0    # define prev_score variable
    
        for idx, x in enumerate(table_data, start = 1):
            
            player_name = x["player name"]
            team_name = x["team name"]
            fixture_total = x["fixture total"]
            gameweek = x["gw"]
            
            # if scores are equal to previous entry, make ranking same
            if idx > 1 and fixture_total == prev_score:
                rank = "="
            else:
                rank = str(idx)
                    
            prev_score = fixture_total     

            print('{:3} {:25} {:>3}  (GW{})'.format(rank, team_name, fixture_total, gameweek))
        print("")
        print("")
        
    ## Scorebord printer function -- ENDS ##
            
    print( "** GW SCORES **")
    print( "" )
    
    print('{:–<41}'.format(''))
    print( "GW" + str(gw_input) + " Rankings" )
    print('{:–<41}'.format(''))
    
    filtered_list_gw = list(filter(lambda d: d["gw"] == gw_input, sorted_list_of_scores))
    print_scoreboard(filtered_list_gw)
            
    print('{:–<41}'.format(''))
    print( "Top 5 Overall" )
    print('{:–<41}'.format(''))
    
    def filter_first_n_unique_scores(n, lst):
        
        scores_filter = []
        count = 0
        
        print("n", n)

        while count < n:
            for x in lst:
                print("count", count)
                fixture_total = x["fixture total"]
                
                if count > n:
                    break
                
                if fixture_total not in scores_filter:
                    scores_filter.append(fixture_total)
                    count += 1

        return scores_filter
    
        
    top_five_filter = filter_first_n_unique_scores(5, sorted_list_of_scores)
    print(top_five_filter)
                
    
    print('{:–<41}'.format(''))
    print( "Bottom 5 Overall" )
    print('{:–<41}'.format(''))

        
create_scoreboards()
            