import json
from collections import Counter

# load database
season_dir = './seasons/2024'	#edit this to target different seasons

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

# create a data object with results data
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
			'chip_played': str(i_database[manager_code]['chip_played_array'][int(item['gw'])-1]),
			'transfers_made': int(i_database[manager_code]['transfers_made_array'][int(item['gw'])-1]),
			'league_pos_after': int(i_database[manager_code]['league_position_array'][int(item['gw'])-1]),
			'league_pos_before': int(i_database[manager_code]['league_position_array'][int(item['gw'])-2]) if int(item['gw']) > 1 else 'n/a',
			'league_pos_change': int(i_database[manager_code]['league_position_array'][int(item['gw'])-2] - i_database[manager_code]['league_position_array'][int(item['gw'])-1]) if int(item['gw']) > 1 else 'n/a',
			'season_win_count': int(i_database[manager_code]['fixture_result_array'][:int(item['gw'])].count('win')),
			'season_loss_count': int(i_database[manager_code]['fixture_result_array'][:int(item['gw'])].count('loss')),
			'season_draw_count': int(i_database[manager_code]['fixture_result_array'][:int(item['gw'])].count('draw')),
		}

		#print(f"{temp_dict}")
		d_players.append(temp_dict)


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
	

# print(d_fixtures)

from collections import Counter

for gw in range(1,gameweeks_played+1):
	print(f"Gameweek {gw}")

	def return_combined_gw_score(gw):
		return sum([x['fixture_score'] for x in d_players if x['gw'] == gw])

	def return_list_of_gameweek_scores(gw):
		return [return_combined_gw_score(x) for x in [x for x in range(1,gw+1)]]

	def return_gw_combined_score_rank(gw):
		return sorted(return_list_of_gameweek_scores(gw), reverse=True).index(return_combined_gw_score(gw))+1
	
	def return_average_gw_score(gw):
		return sum([x['fixture_score'] for x in d_players if x['gw'] == gw]) / len([x['fixture_score'] for x in d_players if x['gw'] == gw])

	def return_combined_gw_transfers_made(gw):
		return sum([x['transfers_made'] for x in d_players if x['gw'] == gw])


	print(f"Total combined points scored: {comma_format(return_combined_gw_score(gw))}")
	print(f"Total combined points ranking: {ord(return_gw_combined_score_rank(gw))}")
	print(f"Average points scored: {comma_format(return_average_gw_score(gw))}")
	print(f"Transfers made: {comma_format(return_combined_gw_transfers_made(gw))}")

	gw_chips = [x['chip_played'] for x in d_players if x['gw'] == gw and x['chip_played'].lower() != 'none']
	print(f"Chips played: {len(gw_chips)}")
	for key,val in Counter(gw_chips).items():
		lst = [x['team_name'] for x in d_players if x['chip_played'] == key]
		print(f"{key}: {val} ({str(', '.join(str(x) for x in lst))})")
		print()




