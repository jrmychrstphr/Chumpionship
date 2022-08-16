import os
import json


#create empty dict to store data
database = {}
third_pass_dict = {}

# First pass (pulled from scraped data)
database_dir = './data'

#where do I want to put this?
database_path = './builders/~ templates/database.json'

for dirpath, dirnames, files in os.walk(database_dir):


	#print(f'Found directory: {dirpath}')
	#print(f'Files: {files}')

	if not dirpath == database_dir:

		existing_gameweeks = []

		#create empty lists for the data to go in
		fixture_score_array = []
		overall_total_points_array = []
		fixture_opponent_array = []
		chip_played_array = []

		transfers_made_array = []
		transfered_in_array = []
		transfered_out_array = []

		captains_array = []

		for file_name in files:

			# open player_info.json
			if file_name == 'player_info.json':

				# pull data from file
				with open(dirpath + "/" + file_name) as f:
					d = json.load(f)

					manager_code = d['manager_code']
					manager_name = d['manager_name']
					team_name = d['team_name']

			# open player_info.json
			elif file_name == 'fixture-list.json':

				# pull data from fixture-list.json
				with open(dirpath + "/fixture-list.json") as f:
					d = json.load(f)

					for gameweek, val in d.items():
						fixture_opponent_array.append(val['opponent_code'])


			#create a list of existing gameweek files
			elif file_name.startswith('GW'):
				existing_gameweeks.append(file_name)

		#sort the list of gameweeks
		existing_gameweeks.sort()


		for file_name in existing_gameweeks:

				# pull data from files
				with open(dirpath + "/" + file_name) as f:
					d = json.load(f)

					fixture_score_array.append(d['fixture_score'])
					overall_total_points_array.append(d['overall_total_points'])
					chip_played_array.append(d['chip_played'])
					transfers_made_array.append(d['transfers_made'])
					transfered_in_array.append(d['transfered_in'])
					transfered_out_array.append(d['transfered_out'])

					for x in d['squad']:
						if x['captain_status'].lower() == 'captain':
							captains_array.append(f"{x['player_name']} ({x['player_position']}, {x['player_team']})")


		database[manager_code] = {}
		database[manager_code]['fpl_code'] = manager_code
		database[manager_code]['manager_name'] = manager_name
		database[manager_code]['team_name'] = team_name
		database[manager_code]['fixture_score_array'] = fixture_score_array
		database[manager_code]['total_score_array'] = overall_total_points_array
		database[manager_code]['fixture_opponent_array'] = fixture_opponent_array
		database[manager_code]['chip_played_array'] = chip_played_array
		
		database[manager_code]['transfers_made_array'] = transfers_made_array
		database[manager_code]['transfered_in_array'] = transfered_in_array
		database[manager_code]['transfered_out_array'] = transfered_out_array
		
		database[manager_code]['captains_array'] = captains_array


#print(database)

# second pass (calculate fixture results, league points)
for manager_code in database:
	d = database.copy()
	#print(d['manager_name'])

	# to write to database
	database[manager_code]['fixture_result_array'] = []
	database[manager_code]['league_points_array'] = []
	database[manager_code]['total_league_points_array'] = []
	database[manager_code]['fixture_margin_array'] = []

	# temporary lists
	fixture_points_array = []
	fixture_margin_array = []

	for count, value in enumerate(d[manager_code]['fixture_score_array']):

		gameweek = "GW" + str("{0:0=2d}".format(int(count+1)))
		score = d[manager_code]['fixture_score_array'][count]
		opponent_score = database[d[manager_code]['fixture_opponent_array'][count]]['fixture_score_array'][count]
		fixture_margin = int(score) - int(opponent_score)

		fixture_margin_array.append(fixture_margin)

		#calculate fixture result
		if fixture_margin > 0:
			database[manager_code]['fixture_result_array'].append('win')
			database[manager_code]['league_points_array'].append(3)
		elif fixture_margin < 0:
			database[manager_code]['fixture_result_array'].append('loss')
			database[manager_code]['league_points_array'].append(0)
		elif fixture_margin == 0:
			database[manager_code]['fixture_result_array'].append('draw')
			database[manager_code]['league_points_array'].append(1)
		else:
			fixture_result = 'error'
			fixture_points_array.append('error')
			print(f'Error calculating result: {d[manager_code]["manager_name"]}, {gameweek}')

		database[manager_code]['total_league_points_array'].append(sum(database[manager_code]['league_points_array']))
		database[manager_code]['fixture_margin_array'] = fixture_margin_array

		# push data to third_pass_dict for calculating league position later
		if gameweek not in third_pass_dict:
			third_pass_dict[gameweek] = []

		temp_league_pos_obj = {
			'manager_code': manager_code,
			'league_points':d[manager_code]['total_league_points_array'][count],
			'total_score': d[manager_code]['total_score_array'][count],
			'fixture_score': d[manager_code]['fixture_score_array'][count]
		}

		third_pass_dict[gameweek].append(temp_league_pos_obj)
		#print(f'{gameweek}: {score} – {opponent_score}... {fixture_result}')

#print(third_pass_dict)

# third pass (calculate league position)
for gameweek, value in third_pass_dict.items():

	d = sorted(value.copy(), key = lambda x: (x['league_points'], x['total_score']), reverse=True)
	for idx, val in enumerate(d):

		manager_code = val['manager_code']

		if idx > 0:
			# if league points and total score  == the previous entry in the array,
			if d[idx]['league_points'] == d[idx-1]['league_points'] and d[idx]['total_score'] == d[idx-1]['total_score']:
				# the position is the same as the previous entry
				pos = pos
			#else, the position is determined by the item's position in the sorted list
			else:
				pos = idx+1
		#the league pos for the first item in the sorted list will always be 1
		else:
			pos = idx+1

		if 'league_position_array' not in database[manager_code]:
			database[manager_code]['league_position_array'] = []

		database[manager_code]['league_position_array'].append(int(pos))

	
	d = sorted(value.copy(), key = lambda x: (x['fixture_score']), reverse=True)
	for idx, val in enumerate(d):

		manager_code = val['manager_code']

		if idx > 0:
			# if fixture_score  == the previous entry in the array,
			if d[idx]['fixture_score'] == d[idx-1]['fixture_score']:
				# the position is the same as the previous entry
				pos = pos
			#else, the position is determined by the item's position in the sorted list
			else:
				pos = idx+1
		#the league pos for the first item in the sorted list will always be 1
		else:
			pos = idx+1

		if 'fixture_score_rank_array' not in database[manager_code]:
			database[manager_code]['fixture_score_rank_array'] = []

		database[manager_code]['fixture_score_rank_array'].append(int(pos))


#print(database)

#save temp json of player info
with open(database_path, 'w') as f:
	json.dump(database, f, sort_keys=True, indent=4, separators=(',', ': '))
	print(f"Saved to: {database_path}")

