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


# print a gameweek-by-gameweek
# analysis of the data
for gw in range(1,gameweeks_played+1):

	def print_divder(): print(f"-------------------")

	print(f"")
	print_divder()
	print(f"--- Gameweek {format_two_digit(gw)} ---")
	print_divder()

	# Gameweek score summary
	def msg_gameweek_score():

		# functions for building the sumary message
		def return_combinedscore(gw):
			return sum([x['fixture_score'] for x in d_players if x['gw'] == gw])
		def return_list_combinedscores(gw):
			return [return_combinedscore(x) for x in [x for x in range(1,gw+1)]]
		def high_low_gw_score_since(gw):

			# Compares current gw combined score to all previous prev_scores
			# and returns a value based on how long has passed since a higher 
			# or lower combined score has been posted

			# Positive value: Highest score since
			# Negative value: Lowest score since
			# False: No result (eg, highest/lowest of the season)

			prev_scores = list(reversed(return_list_combinedscores(gw)))
			gw_score = return_combinedscore(gw)
			
			# prev_scores = [12,1,2,3,4,5,6,7,8,9,10,11]
			# gw_score = prev_scores[0]
			
			lower = next((x for x in prev_scores[1:] if x <= gw_score), False)
			higher = next((x for x in prev_scores[1:] if x >= gw_score), False)

			if lower and lower > 1:
				res = -(prev_scores[1:].index(lower)+1)
			elif higher and higher > 1:
				res = (prev_scores[1:].index(higher)+1)
			else:
				res = False
			return res
		def return_combinedscore_rank(gw):
			return sorted(return_list_combinedscores(gw), reverse=True).index(return_combinedscore(gw))+1
		def return_average_gw_score(gw):
			return sum([x['fixture_score'] for x in d_players if x['gw'] == gw]) / len([x['fixture_score'] for x in d_players if x['gw'] == gw])

		# build the message
		msg = f"Round {gw}"

		if return_combinedscore_rank(gw) == 1:
			msg += f" was the highest-scoring week of the season so far."
		
		elif return_combinedscore_rank(gw) >= len(return_list_combinedscores(gw)) and gw > 2:
			msg += f" was the lowest-scoring week of the season so far."
		
		elif return_combinedscore_rank(gw) <= 5:
			msg += f" was the {ord(return_combinedscore_rank(gw))} highest-scoring week of the season so far."
		
		elif high_low_gw_score_since(gw) and high_low_gw_score_since(gw) > 2:
			msg += f" was the highest-scoring week for {abs(high_low_gw_score_since(gw))} rounds."
		
		elif high_low_gw_score_since(gw) and high_low_gw_score_since(gw) < -2:
			msg += f" was the lowest-scoring week for {abs(high_low_gw_score_since(gw))} rounds."




		
		msg += f" Chumpionship teams scored a combined {comma_format(int(return_combinedscore(gw)))} points"
		
		if gw > 1:
			score_diff = return_combinedscore(gw) - return_combinedscore(gw-1)
			if score_diff == 0:
				msg += f" – the same score as"
			if score_diff > 0:
				msg += f" – {comma_format(int(score_diff))} more than in"
			if score_diff < 0:
				msg += f" – {comma_format(int(-score_diff))} fewer than in"

			msg += f" GW{gw-1} –"

		msg += f" with an average score of {comma_format(return_average_gw_score(gw))}."

		return msg
	print(msg_gameweek_score())
	
	# Gameweek transfers
	def msg_transfers():

		def return_combinedtransfersmade(gw):
			return sum([x['transfers_made'] for x in d_players if x['gw'] == gw])

		l_transfers = [return_combinedtransfersmade(x) for x in [x for x in range(1,gw+1)]]

		msg = f""

		
		if gw == 2:
			msg += f"The first transfer window of the campaign saw"
			msg += f" {comma_format(int(return_combinedtransfersmade(gw)))} changes"
		
		elif return_combinedtransfersmade(gw) == max(l_transfers):
			msg += f"The busiest transfer window so far saw"
			msg += f" {comma_format(int(return_combinedtransfersmade(gw)))} changes"
		
		else:
			msg += f"{comma_format(int(return_combinedtransfersmade(gw)))} changes were"
	
		msg += f" made to Chumpionship sides ahead of the GW{int(gw)} deadline."

		if gw > 1: return msg
	if msg_transfers(): print(msg_transfers())	

	# Chips played this gameweek
	def msg_chips():
		msg = f""

		l_gw_chips = [x['chip_played'] for x in d_players if x['gw'] == gw and x['chip_played'].lower() != 'none']


		gw_chip_count = len(l_gw_chips)
		gw_chip_dict = collections.Counter(l_gw_chips)

		if gw_chip_count == 0:
			return False

		if len(gw_chip_dict) == 1:
			for key,val in gw_chip_dict.items():
				msg += f"{written_number(int(val)).title()} team"
				if val > 1: msg += f"s"
				msg += f" played a {key.title()}"

		else:
			msg += f"{written_number(int(gw_chip_count)).title()} teams played a chip:"

			for i,x in enumerate(gw_chip_dict.most_common()):
				chip_name = str(x[0])
				val = int(x[1])

				if i != 0: msg += f";"
				msg += f" {chip_name}: {val}"


		return msg
	if msg_chips(): print(msg_chips())

	# Captains played this gameweek
	def msg_captains():
		msg = f""

		#Isak (5pts before captain bonus) was the league's most popular skipper, wearing 10 Chumpionship armbands in Week 1. 
		#M.Salah (14pts), and Haaland (7pts) wore three armbands each; 
		#while Mateta (1pt), Al-Hamadi (1pt), Solanke (2pts), and B.Fernandes (3pts) wore 1 armband apiece.

		# name: 
		# score:
		# occurrances:
		

		#create a list of gameweek captains data
		caps_data = []

		data = [x for x in d_players if x['gw'] == gw]

		for x in data:
			dict = {
				"name": str(x['captain']),
			}

			if "captain" in x['chip_played'].lower() :
				dict["score"] = int(x['captain_points']/3)
			else:
				dict["score"] = int(x['captain_points']/2)

			caps_data.append(dict)

		# print("caps_data")
		# print(caps_data)

		result = {}
		for item in caps_data:
			name = item['name']
			if name not in result:
				result[name] = {'count': 1, **item}
			else:
				result[name]['count'] += 1

		caps_data = list(result.values())
		
		# Extract unique scores
		unique_counts = {item['count'] for item in result.values()}
		unique_counts = sorted(list(unique_counts), reverse=True)

		# print("caps_data")
		# print(caps_data)

		# print("unique_counts")
		# print(unique_counts)

		msg += f"{written_number(len(caps_data)).title()} different players were given the armband by Chumpionship teams in Week {gw}. "

		for idx,count in enumerate(unique_counts):
			matches = [cap for cap in caps_data if cap['count'] == count]
			matches.sort(key=lambda x: x['score'], reverse=True)
			# print("count")
			# print(count)
			# print("matches")
			# print(matches)
			# print(len(matches))

			for i,match in enumerate(matches):
				name = match['name']
				score = match['score']
				msg += f"{name} ({score}pts)"


				# add commas if more than one match
				if len(matches) > 1:
					if i+2 == len(matches):
						msg += f", and "
					elif i+1 == len(matches): 
						msg += f""
					else:
						msg += f", "

			
			if idx == 0:
				if len(matches) == 1: 
					msg += f" was the league's most popular choice"
				else: 
					msg += f" were the league's most popular choice"
						
				msg += f" – wearing {written_number(count)} armbands"
			elif count > 1:
				msg += f" wore {written_number(count)} armbands"
			else:
				msg += f" wore {written_number(count)} armband"


			if len(matches) > 1:
				msg += f" each"
				
			msg += f". "
		
		return msg
	if msg_captains(): print(msg_captains())

	# Highest-scoring fixture(s)
	def msg_hiscorefix():
		szn_hi_score = max([x['total_points_scored'] for x in d_fixtures if x['gw'] <= gw])
		gw_hi_score = max([x['total_points_scored'] for x in d_fixtures if x['gw'] == gw])

		fixtures = [x for x in d_fixtures if x['gw'] == gw and x['total_points_scored'] == gw_hi_score]

		msg = f""

		for fix in fixtures:
			home = [x for x in d_players if x['gw'] == gw and x['manager_code'] == str(fix['home_manager_code'])][0]
			away = [x for x in d_players if x['gw'] == gw and x['manager_code'] == str(fix['away_manager_code'])][0]
			
			msg += f"{home['team_name']} and {away['team_name']}"
			msg += f" combined for {int(gw_hi_score)}pts in the"
			msg += f" highest-scoring fixture of Round {gw}."

			if gw_hi_score == szn_hi_score:
				msg += f" It was also the highest-scoring fixture of the season so far."
	
		return msg
	if msg_hiscorefix(): print(msg_hiscorefix())

	# Lowest-scoring fixture(s)
	def msg_loscorefix():
		szn_lo_score = min([x['total_points_scored'] for x in d_fixtures if x['gw'] <= gw])
		gw_lo_score = min([x['total_points_scored'] for x in d_fixtures if x['gw'] == gw])

		fixtures = [x for x in d_fixtures if x['gw'] == gw and x['total_points_scored'] == gw_lo_score]

		msg = f""

		for fix in fixtures:
			home = [x for x in d_players if x['gw'] == gw and x['manager_code'] == str(fix['home_manager_code'])][0]
			away = [x for x in d_players if x['gw'] == gw and x['manager_code'] == str(fix['away_manager_code'])][0]
			
			msg += f"{home['team_name']} and {away['team_name']}"
			msg += f" combined for {int(gw_lo_score)}pts in the"
			msg += f" lowest-scoring fixture of Round {gw}."

			if gw_lo_score == szn_lo_score:
				msg += f" It was also the lowest-scoring fixture of the season so far."
	
		return msg
	if msg_loscorefix(): print(msg_loscorefix())

	# Highest-scoring loser(s)
	def msg_hiscorewinner():
		score = max([x['fixture_score'] for x in d_players if x['gw'] == gw and x['fixture_result'] == 'loss'])
		results = [x for x in d_players if x['gw'] == gw and x['fixture_result'] == 'loss' and x['fixture_score'] == score]

		msg = f""

		for x in results:

			opp = [o for o in d_players if o['gw'] == gw and o['manager_code'] == x['fixture_opponent']][0]

			msg += f"{x['manager_name']} was the highest-scoring loser of Round {gw}."
			msg += f" {x['team_name']} were beaten by {opp['team_name']}"
			msg += f" despite a score of {int(x['fixture_score'])}."

		return msg
	if msg_hiscorewinner(): print(msg_hiscorewinner())

	# Lowest-scoring winner(s)
	def msg_loscorewinner():
		score = min([x['fixture_score'] for x in d_players if x['gw'] == gw and x['fixture_result'] == 'win'])
		results = [x for x in d_players if x['gw'] == gw and x['fixture_result'] == 'win' and x['fixture_score'] == score]

		msg = f""

		for x in results:

			opp = [o for o in d_players if o['gw'] == gw and o['manager_code'] == x['fixture_opponent']][0]

			msg += f"{x['manager_name']} was the lowest-scoring winner of Round {gw}."
			msg += f" {x['team_name']} beat {opp['team_name']}"
			msg += f" with a tally of {int(x['fixture_score'])}."

		return msg
	if msg_loscorewinner(): print(msg_loscorewinner())

	#Highest score
	def msg_hiscore():
		score = max([x['fixture_score'] for x in d_players if x['gw'] == gw])
		results = [x for x in d_players if x['gw'] == gw and x['fixture_score'] == score]

		msg = f""

		if len(results) > 1:
			msg += f"{written_number(len(results)).title()} bosses topped the scoreboard in GW{int(gw)}: "

		for idx,x in enumerate(results):


			count = len([c for c in d_players if c['gw'] <= gw and c['manager_code'] == x['manager_code'] and c['fixture_score_rank'] == 1])

			msg += f"{x['manager_name']} topped the scoreboard"
			msg += f" for the {ord(int(count))} time this season"
			msg += f" with a haul of {int(x['fixture_score'])}"
			
			if len(results) > 1: 
				msg += f"; "
			else:
				msg += f"."

		szn_top = max([x['fixture_score'] for x in d_players if x['gw'] <= gw])
		prev = max([x['fixture_score'] for x in d_players if x['gw'] <= gw])

		if score == szn_top:
			msg += f" This is a new season-high score."

		return msg
	if msg_hiscore(): print(msg_hiscore())

	def msg_fixmargin():
		value = max([x['fixture_margin'] for x in d_players if x['gw'] == gw])
		results = [x for x in d_players if x['gw'] == gw and x['fixture_margin'] == value]

		season_hi = max([x['fixture_margin'] for x in d_players if x['gw'] <= gw])

		if len(results) == 0:
			return
		
		msg = f""

		for x in results:
			opponent_name = [a['manager_name'] for a in d_players if a['manager_code'] == x['fixture_opponent']][0]

			msg += f"{x['manager_name']} enjoyed the biggest win of GW{int(gw)}"

			if value == season_hi:
				msg += f" – and largest winning margin of the season –"

			msg += f" beating {opponent_name} by +{int(x['fixture_margin'])}"

			if len(results) > 1: msg += f"\n"

		return msg
	if msg_fixmargin(): print(msg_fixmargin())

	def list_managercodes():
		results = []
		for x in d_players:
			if x['manager_code'] not in results:
				results.append(x['manager_code'])
		return results

	def msg_pbscores():

		results = []

		for manager_code in list_managercodes():
			score = max([x['fixture_score'] for x in d_players if x['gw'] <= gw and x['manager_code'] == manager_code])
			r = [x for x in d_players if x['gw'] == gw and x['manager_code'] == manager_code and x['fixture_score'] == score]

			for r in r:
				results.append(r)
		
		results.sort(key=lambda x: x.get('fixture_score'), reverse=True)

		if len(results) == 0:
			return
		
		msg = f""
		
		msg += f"{written_number(int(len(results))).title()} manager"
		if len(results) > 1: msg += f"s"
		msg += f" posted their highest score of the season so far:"

		for x in results:
			msg += f"\n"
			msg += f"\t * {x['manager_name']}: {int(x['fixture_score'])}"
			msg += f""

		return msg


	if msg_pbscores(): print(msg_pbscores())

	def msg_pwscores():

		results = []

		for manager_code in list_managercodes():
			score = min([x['fixture_score'] for x in d_players if x['gw'] <= gw and x['manager_code'] == manager_code])
			r = [x for x in d_players if x['gw'] == gw and x['manager_code'] == manager_code and x['fixture_score'] == score]

			for r in r:
				results.append(r)

		results.sort(key=lambda x: x.get('fixture_score'), reverse=False)

		if len(results) == 0:
			return
		
		msg = f""

		msg += f"{written_number(int(len(results))).title()} manager"
		if len(results) > 1: msg += f"s"
		msg += f" posted their lowest score of the season so far:"

		for x in results:
			msg += f"\n"
			msg += f"\t* {x['manager_name']}: {int(x['fixture_score'])}"
			msg += f""

		return msg


	if msg_pwscores(): print(msg_pwscores())



