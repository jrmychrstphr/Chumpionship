import json
import collections

# load database
season_dir = './seasons/2025'	#edit this to target different seasons

database_path = season_dir + '/data/database.json'
fixtures_path = season_dir + '/data/season_fixture_list.json'

with open(database_path) as f:
	i_database = json.load(f)

with open(fixtures_path) as f:
	i_fixtures = json.load(f)

##########################################
# useful functions
def ord(n):
    return str(n)+("th" if 4<=n%100<=20 else {1:"st",2:"nd",3:"rd"}.get(n%10, "th"))

def comma_format(n):
 	 return ("{:,}".format(n))

def format_two_digit(n):
	return str("{0:0=2d}".format(int(n)))

def written_number(n):
	numbers = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
	if int(n) < 10:
		return str(numbers[int(n)])
	else:
		return str(n)


d_fixtures = []
d_players = []

gameweeks_played =  min([len(i_database[x]['fixture_score_array']) for x in i_database.keys()])

# populate 'd_fixtures' with empty dicts
# for each fixture already played
for idx, val in enumerate([i_fixtures[x] for x in i_fixtures.keys() if int(x) <= gameweeks_played]):
	for v in val:
		temp_dict = {
			'gw': int(idx+1),
			'total_points_scored': 0,
			'fixture_margin': 0,
			'league_pos_before_difference': 0,
			'home_manager_code': str(v['home_team']),
			'away_manager_code': str(v['away_team']),
		}

		d_fixtures.append(temp_dict)

# populate 'd_players' with data
for item in [x for x in d_fixtures]:
	#print(f"{item['gw']}")
	players = [item['home_manager_code'],item['away_manager_code']]
	for manager_code in players:

		#print(f"{manager_code}")

		temp_dict = {
			'gw': int(item['gw']),
			'manager_code': str(manager_code),
			'manager_name': str(i_database[manager_code]['manager_name']),
			'team_name': str(i_database[manager_code]['team_name']),
			'fixture_opponent': str("".join(str(x) for x in players if x != str(manager_code))),
			'fixture_score': float(i_database[manager_code]['fixture_score_array'][int(item['gw'])-1]),
			'fixture_result': str(i_database[manager_code]['fixture_result_array'][int(item['gw'])-1]),
			'fixture_margin': float(i_database[manager_code]['fixture_margin_array'][int(item['gw'])-1]),
			'fixture_score_rank': int(i_database[manager_code]['fixture_score_rank_array'][int(item['gw'])-1]),
			'total_season_score': float(i_database[manager_code]['total_score_array'][int(item['gw'])-1]),
			'captain': str(i_database[manager_code]['captains_array'][int(item['gw'])-1]),
			'captain_points': int(i_database[manager_code]['captains_points_array'][int(item['gw'])-1]),
			'chip_played': str(i_database[manager_code]['chip_played_array'][int(item['gw'])-1]),
			'transfers_made': int(i_database[manager_code]['transfers_made_array'][int(item['gw'])-1]),
			'league_pos_after': int(i_database[manager_code]['league_position_array'][int(item['gw'])-1]),
			'league_pos_before': int(i_database[manager_code]['league_position_array'][int(item['gw'])-2]) if int(item['gw']) > 1 else 'n/a',
			'league_pos_change': int(i_database[manager_code]['league_position_array'][int(item['gw'])-2] - i_database[manager_code]['league_position_array'][int(item['gw'])-1]) if int(item['gw']) > 1 else 'n/a',
			'season_win_count': int(i_database[manager_code]['fixture_result_array'][:int(item['gw'])].count('win')),
			'season_loss_count': int(i_database[manager_code]['fixture_result_array'][:int(item['gw'])].count('loss')),
			'season_draw_count': int(i_database[manager_code]['fixture_result_array'][:int(item['gw'])].count('draw')),

			'bench_score': float(i_database[manager_code]['bench_score_array'][int(item['gw'])-1]),
		}

		#print(f"{temp_dict}")
		d_players.append(temp_dict)

# update 'd_fixtures' with data from 'd_players'
for fixture in d_fixtures:
	players = [fixture['home_manager_code'], fixture['away_manager_code']]
	fixture_gw = fixture['gw']

	scores,pos = [],[]

	for x in [x for x in d_players if x['gw']==fixture_gw and x['manager_code'] in players]:
		scores.append(x['fixture_score'])
		pos.append(x['fixture_score']) if fixture_gw != 1 else ''
	
	fixture.update({"total_points_scored": sum(scores)})
	fixture.update({"fixture_margin": max(scores)-min(scores)})
	fixture.update({"league_pos_before_difference": max(pos)-min(pos)}) if fixture_gw != 1 else ''
	
#print(d_fixtures)
#print(d_players)

print(set([x['chip_played'] for x in d_players ]))

"""
Chip-free chief (£20) 🙌
The highest single-week score of the season 
that is achieved without a chip will earn £20.
"""

print(f"Chip-free chief (£20)")

#filter to just entries with the chip
entries = [x for x in d_players if x['chip_played'] == "None"]

if len(entries) == 0:
	print(f"No relevant scores have been set")
else:
	print(f"{len(entries)} 'chip-free' scores have been set so far...")
	top_score = max([x['fixture_score'] for x in entries])
	print(f"The highest chip-free score set so far is {int(top_score)}pts")
	results = [x for x in entries if x['fixture_score'] == top_score]
	print(f"This score has been met {len(results)} times:")	
	for x in results:
		print(f"\t{x['manager_name']} ({int(x['fixture_score'])}pts): GW{x['gw']}")

print(f"")
print(f"")

"""
Free Hit hero (£20)🦸
The highest single-week score of the season when 
playing a Free Hit chip will win £20.
"""

print(f"Free Hit hero (£20)")

#filter to just entries with the chip
entries = [x for x in d_players if x['chip_played'] == "Free Hit"]

if len(entries) == 0:
	print(f"No relevant scores have been set")
else:
	print(f"{len(entries)} 'Free Hit' scores have been set so far...")
	top_score = max([x['fixture_score'] for x in entries])
	print(f"The highest 'Free Hit' score set so far is {int(top_score)}pts")
	results = [x for x in entries if x['fixture_score'] == top_score]
	print(f"This score has been met {len(results)} times:")	
	for x in results:
		print(f"\t{x['manager_name']} ({int(x['fixture_score'])}pts): GW{x['gw']}")

print(f"")
print(f"")

"""
Bench Boost boss (£20)👔
The highest scoring bench of the season when playing 
a Bench Boost chip will bag £20. Only points scored by 
players who end the gameweek sat on your bench – after 
auto subs – will count towards this. So watch out for 
injuries, suspensions and no-shows in your starting XI.
"""

print(f"Bench Boost Boss")

#filter to just entries with the chip
entries = [x for x in d_players if x['chip_played'] == "Bench Boost"]

if len(entries) == 0:
	print(f"No relevant scores have been set")
else:
	print(f"{len(entries)} 'Free Hit' scores have been set so far...")
	top_score = max([x['bench_score'] for x in entries])
	print(f"The highest 'Free Hit' score set so far is {int(top_score)}pts")
	results = [x for x in entries if x['bench_score'] == top_score]
	print(f"This score has been met {len(results)} times:")	
	for x in results:
		print(f"\t{x['manager_name']} ({int(x['bench_score'])}pts): GW{x['gw']}")

print(f"")
print(f"")

"""
Triple Captain crown (£20)👑
The season's highest scoring captain when playing a 
Triple Captain chip will take home £20.  Scores by Vice 
Captains will not count if a Captain fails to score, so 
make sure your armband is given to someone who's fit, 
healthy and playing! 

"""

print(f"Triple Captain Crown")

#filter to just entries with the chip
entries = [x for x in d_players if x['chip_played'] == "Triple Captain"]

if len(entries) == 0:
	print(f"No relevant scores have been set")
else:
	print(f"{len(entries)} 'Triple Captain' scores have been set so far...")
	top_score = max([x['captain_points'] for x in entries])
	print(f"The highest 'Triple Captain' score set so far is {int(top_score)}pts")
	results = [x for x in entries if x['captain_points'] == top_score]
	print(f"This score has been met {len(results)} times:")	
	for x in results:
		print(f"\t{x['manager_name']} ({x['captain']}, {int(x['captain_points'])}pts): GW{x['gw']}")

print(f"")
print(f"")