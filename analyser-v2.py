import json
from collections import Counter

# load database
database_dir = './seasons/2023/builders/~ templates'
database_path = database_dir + '/database.json'

with open(database_path) as f:
	data = json.load(f)

# useful functions
def ord(n):
    return str(n)+("th" if 4<=n%100<=20 else {1:"st",2:"nd",3:"rd"}.get(n%10, "th"))

# define gameweeks
def return_gameweeks(n):
	n = str(n)
	l = n.split("-")

	if len(l) < 3: g = list(range(int(l[0]),int(l[-1])+1))
	else: g = False

	print(f"gameweeks = {g}")
	return g

gameweeks = return_gameweeks("26")

# compile dataset

dataset = []
teams = {}

"""

Gameweek stats:
+ total points scored
+ chips played 


Player stats:
+ GW score
+ GW score rank (ie, Player X scored the nth-best score of the GW)
+ GW score rank count (ie, Player X has been nth-best score of the GW i times this season)
+ Player score rank (ie, Player Xs nth-best socre of the season)
+ Overall score
+ Games since defeat / win
+ Chips played
+ League position before game
+ League position now (after game)
+ Change in league position
+ Highest / lowest position in n GWs
+ Position thresholds (eg, Leader, top-four, top-half, bottom-three)
+ Fixture margin
+ Fixture margin rank, GW (ie, biggest win of the Round)
+ Fixture margin, league rank (ie, the biggest win / heaviest defeat of the entire season so far)
+ Fixture margin, personal rank (ie, Player X's biggest win / heaviest defeat of the season so far)


"""



for key, val in data.items():

	teams[val['fpl_code']] = {
		'manager_name': val['manager_name'],
		'team_name': val['team_name'],		
	}

	d_obj = {

		#player info
		'manager_code': val['fpl_code'],
		'manager_name': val['manager_name'],
		'team_name': val['team_name'],
		'opponents': val['fixture_opponent_array'],


		# data across gameweeks range
		'range_fixture_scores': val['fixture_score_array'][gameweeks[0]-1:gameweeks[-1]],
		'range_total_score': sum(val['fixture_score_array'][gameweeks[0]-1:gameweeks[-1]]),
		'range_highest_fixture_score': max(val['fixture_score_array'][gameweeks[0]-1:gameweeks[-1]]),
		'range_lowest_fixture_score': min(val['fixture_score_array'][gameweeks[0]-1:gameweeks[-1]]),
		'range_fixture_margins': val['fixture_margin_array'][gameweeks[0]-1:gameweeks[-1]],
		'range_highest_fixture_margin': max(val['fixture_margin_array'][gameweeks[0]-1:gameweeks[-1]]),
		'range_league_positions': val['league_position_array'][gameweeks[0]-1:gameweeks[-1]],
		'range_chips_played': val['chip_played_array'][gameweeks[0]-1:gameweeks[-1]],
		'range_transfers_made': val['transfers_made_array'][gameweeks[0]-1:gameweeks[-1]],
		'range_total_transfers_made': sum(val['transfers_made_array'][gameweeks[0]-1:gameweeks[-1]]),
		'range_transfered_in': val['transfered_in_array'][gameweeks[0]-1:gameweeks[-1]],
		'range_transfered_out': val['transfered_out_array'][gameweeks[0]-1:gameweeks[-1]],
		'range_captains': val['captains_array'][gameweeks[0]-1:gameweeks[-1]],
		'range_league_positions': val['league_position_array'][gameweeks[0]-1:gameweeks[-1]],


		# data at the end of gameweeks range (ie, season so far)
		'season_fixture_scores': val['fixture_score_array'][:gameweeks[-1]],
		'season_total_score': sum(val['fixture_score_array'][:gameweeks[-1]]),
		'season_highest_fixture_score': max(val['fixture_score_array'][:gameweeks[-1]]),
		'season_lowest_fixture_score': min(val['fixture_score_array'][:gameweeks[-1]]),
		'season_fixture_margins': val['fixture_margin_array'][:gameweeks[-1]],
		'season_highest_fixture_margin': max(val['fixture_margin_array'][:gameweeks[-1]]),
		'season_league_positions': val['league_position_array'][:gameweeks[-1]],
		'season_chips_played': val['chip_played_array'][:gameweeks[-1]],
		'season_league_positions': val['league_position_array'][:gameweeks[-1]],

	}

	dataset.append(d_obj)

print(dataset)

