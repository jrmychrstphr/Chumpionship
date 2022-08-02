import json
from pathlib import Path


###############
# Loads a .json file from the same directory as this script file #
# returns the result  #

def return_load_json_file(filename):

	print("loading file... ", filename)

	try:
		f = open(filename)
		json_data = json.load(f)
		f.close()

	except:
		print("Error: Failed to load file")
	else:
		print("Success!")
		return json_data


##############
# Searches 'player_data' in database #
# Creates a list of all 'fpl_code' values #
# Returns the result #

def return_manager_codes_as_list():

	manager_codes = []

	#create a list contaiing the FPL code of every manager in the database
	for key, val in database['player_data'].items():

		manager_fpl_code = val['manager_info']['fpl_code']
		manager_codes.append(manager_fpl_code)

	return manager_codes


###############
# Searches 'player_data' in database #
# Returns the value of 'team_name' #
# for the player with defined 'manager_code' #

def return_lookup_team_name(manager_code):

	for key, val in database['player_data'].items():

		idx = key 
		#print('key: ', key)

		if val['manager_info']['fpl_code'] == manager_code:
			team_name = val['manager_info']['team_name']
			return team_name


###############
# Searches 'player_data' in database #
# Returns the value of 'manager_fullname' #
# for the player with defined 'manager_code' #

def return_lookup_manager_fullname(manager_code):

	for key, val in database['player_data'].items():

		if val['manager_info']['fpl_code'] == manager_code:
			manager_fullname = val['manager_info']['manager_fullname']
			return manager_fullname



def push_to_database(input_data):

	for key, val in input_data.items():

		manager_code = key
		performance_data = val

		database['player_data'][manager_code]['performance_data'] = val



###############
# write data to json file
def write_to_json_file(filename, input_data):
    with open(filename + '.json', 'w') as json_file:
        json.dump(input_data, json_file, sort_keys=True, indent=4, separators=(',', ': '))



###############
# compiles season_perfomance  #
# using data from gw_performance (input_data) #
# for each manager in the dataset #
def return_compile_season_performance(input_data):

	#print(input_data)

	# declare a dict to store the output data
	output_data = {}


	# for each player
	for key, val in input_data.items():

		manager_code = key
		gw_performance_data = val


		season_performance = {}

		#declare lists / arrays to store data
		transfers_made_array = []
		fixture_score_array = []
		points_scored_array = []
		points_spent_array = []
		points_on_bench_array = []
		opponent_score_array = []

		fixture_score_running_total_array = []
		
		result_array = []

		# for each gameweek
		for key, val in gw_performance_data.items():

			gw = key

			# push data to arrays

			transfers_made_array.append(val['transfers_made'])
			points_scored_array.append(val['points_scored'])
			points_spent_array.append(val['points_spent'])
			points_on_bench_array.append(val['points_on_bench'])
			fixture_score_array.append(val['fixture_score'])

			fixture_score_running_total_array.append(sum(fixture_score_array))
			
			result_array.append(val['fixture_result'])

			opponent_code = val['fixture_opponent_manager_code']
			opponent_score = input_data[opponent_code][gw]['fixture_score']

			opponent_score_array.append(opponent_score)


		# use arrays to calculate totals

		transfers_made_total = sum(transfers_made_array)
		season_performance['transfers_made_array'] = transfers_made_array
		season_performance['transfers_made_total'] = transfers_made_total

		fixture_score_total = sum(fixture_score_array)
		season_performance['fixture_score_array'] = fixture_score_array
		season_performance['fixture_score_total'] = fixture_score_total

		season_performance['fixture_score_running_total_array'] = fixture_score_running_total_array

		points_scored_total = sum(points_scored_array)
		season_performance['points_scored_array'] = points_scored_array
		season_performance['points_scored_total'] = points_scored_total

		points_spent_total = sum(points_spent_array)
		season_performance['points_spent_array'] = points_spent_array
		season_performance['points_spent_total'] = points_spent_total

		points_on_bench_total = sum(points_on_bench_array)
		season_performance['points_on_bench_array'] = points_on_bench_array
		season_performance['points_on_bench_total'] = points_on_bench_total

		opponent_score_total = sum(opponent_score_array)
		season_performance['opponent_score_array'] = opponent_score_array
		season_performance['opponent_score_total'] = opponent_score_total


		result_count = {}
		result_count['W'] = result_array.count('W')
		result_count['D'] = result_array.count('D')
		result_count['L'] = result_array.count('L')

		season_performance['result_array'] = result_array
		season_performance['result_count'] = result_count


		league_points_array = []
		league_points_running_total_array = []

		for x in result_array:
			if x == 'W':
				p = 3
			elif x == 'L':
				p = 0
			elif x == 'D':
				p = 1
			else:
				print('Error!')

			league_points_array.append(p)
			league_points_running_total_array.append(sum(league_points_array))


		league_points_total = sum(league_points_array)
		season_performance['league_points_array'] = league_points_array
		season_performance['league_points_total'] = league_points_total
		season_performance['league_points_running_total_array'] = league_points_running_total_array


		output_data[manager_code] = season_performance


	## calculate round-by-round league position
	
	# determine how many gameweeks the dataset contains
	manager_codes_list = return_manager_codes_as_list()
	gameweek_array = []

	# declare a dict to store round-by-round pos data for each manager
	temp_league_pos_data = {}

	for key, val in input_data[manager_codes_list[0]].items():
		gameweek_array.append(key)


	# for each gameweek in the data:
	for i in range(len(gameweek_array)):

		gameweek = gameweek_array[i]


		# declare an empty array
		g = []

		# for each manager in the league:
		for manager_code in manager_codes_list:

			# push a dict with:
			m = {}
			
			# manager code
			m['manager_code'] = manager_code
			# total league points
			m['league_points'] = output_data[manager_code]['league_points_running_total_array'][i]
			# total score
			m['total_score'] = output_data[manager_code]['fixture_score_running_total_array'][i]

			g.append(m)


		# order the array by (1) league points, (2) overall score
		g = sorted(g, key = lambda x: (x['league_points'], x['total_score']), reverse=True)

		# use the ordered array to determine league position that gameweek
		for idx, x in enumerate(g):

			manager_code = g[idx]['manager_code']



			if idx > 0:

				# if league points and total score  == the previous entry in the array,
				if g[idx]['league_points'] == g[idx-1]['league_points'] and g[idx]['total_score'] == g[idx-1]['total_score']:
					# the position is the same as the previous entry
					pos = pos

				#else, the position is determined by the item's position in the sorted list
				else:
					pos = idx+1

			#the league pos for the first item in the sorted list will always be 1
			else:
				pos = idx+1

			# if the temp_dict doesn't contain a key matching the manager_code
			if manager_code not in temp_league_pos_data:
				# add that key, and blank array to store league pos data
				temp_league_pos_data[manager_code] = []

			# push the league pos to that manager's array
			temp_league_pos_data[manager_code].append(pos)

	for key, val in temp_league_pos_data.items():

		manager_code = key

		output_data[manager_code]['league_position_array'] = val
		output_data[manager_code]['league_position_now'] = val[-1]

		def return_gameweeks_at_positon(pos):

			output = []

			for idx, v in enumerate(val):
				if v == pos:
					output.append(idx+1)

			return output


		output_data[manager_code]['league_position_high'] = {}
		output_data[manager_code]['league_position_high']['position'] = min(val)
		output_data[manager_code]['league_position_high']['gameweeks_at_position'] = return_gameweeks_at_positon(min(val))


		output_data[manager_code]['league_position_low'] = {}
		output_data[manager_code]['league_position_low']['position'] = max(val)
		output_data[manager_code]['league_position_low']['gameweeks_at_position'] = return_gameweeks_at_positon(max(val))


	return output_data



def covid_fix(input_data):

	# takes gw_performance data (input_data)
	# removes data for GW30 - 38 
	# replaces with data from GW39 - 47 if it exists

	output_data = {}

	# remove data for GW30+ from output
	for key, val in input_data.items():
		output_data[key] = {}
		for k, v in val.items():
			if int(k) < 30:
				output_data[key][k] = v
			elif int(k) < 39:
				if str("{0:0=2d}".format(int(k)+9)) in val.items():
					output_data[key][k] = input_data[key][str("{0:0=2d}".format(int(k)+9))]

	return output_data



def execute():
	global database
	database = return_load_json_file('2020_season_data.json')

	performance_data = return_load_json_file('temp_performance_data.json')

	print(covid_fix(performance_data))
	#print(return_complie_season_performance(performance_data))




execute()
