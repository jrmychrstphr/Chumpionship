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


##########
# Returns the fixture score of a given manager in a given week
def return_lookup_fixture_score (manager_code, gameweek):
	for key, val in database['player_data'].items():
		#print(val)
		if key == manager_code:
			fixture_score = val['gw_performance'][gameweek]['fixture_score']
			return int(fixture_score)


##########
# Returns the fixture result of a given manager in a given week
def return_lookup_fixture_result (manager_code, gameweek):
	for key, val in database['player_data'].items():
		if key == manager_code:

			fixture_result = val['gw_performance'][gameweek]['fixture_result']
			return fixture_result



def return_team_names_as_list():

	team_names = []

	#create a list contaiing the FPL code of every manager in the database
	for key, val in database['player_data'].items():

		team_name = val['manager_info']['team_name']
		team_names.append(team_name)

	return team_names

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




def write_results():

	# create a list of completed gameweeks
	# by using keys from a manager's gw_performance dataset

	completed_gameweeks = []
	manager_code_list = return_manager_codes_as_list()

	for key, val in database['player_data'][manager_code_list[0]]['gw_performance'].items():
		completed_gameweeks.append(key)

	# print(completed_gameweeks)

	for gameweek, fixtures_that_gameweek in database['fixture_list'].items():

		# check if gameweek key appears in completed_gameweeks list
		if gameweek in completed_gameweeks:

			# print(gameweek, ' is in the list')

			# define the name for the file
			filename = 'assets/plain_text_assets/' + gameweek + '---results.txt'

			# create a new .txt file
			f = open(filename,'w+')

			# declare an array / list to store 
			# line-by-line content to write to the file
			file_content = []

			# create file title line
			title_line = 'Chumpionship 2020 - GW' + gameweek + ' results'
			blank_line = ''

			## declare size of fixture line blocks:

			# block at start and end of each line
			# (*).. / (00). / .....
			indent_block_length = 5

			# block for score, etc
			# .000 / ....
			score_block_length = 4

			# max length of a team name
			team_name_block = len(max(return_team_names_as_list(), key=len))

			#store the fixture lines in a temp array / list
			fixture_lines_list = []

			for fixture in fixtures_that_gameweek:

				line = ''

				home_team_name = fixture['H']['team_name']
				home_manager_code = fixture['H']['manager_code']
				home_team_indent = team_name_block - len(home_team_name)


				away_team_name = fixture['A']['team_name']
				away_manager_code = fixture['A']['manager_code']
				away_team_indent = team_name_block - len(away_team_name)

				home_fixture_score = return_lookup_fixture_score(home_manager_code, gameweek)
				away_fixture_score = return_lookup_fixture_score(away_manager_code, gameweek)

				home_fixture_result = return_lookup_fixture_result(home_manager_code, gameweek)
				away_fixture_result = return_lookup_fixture_result(away_manager_code, gameweek)


				def create_indent_block(home_or_away):
					if home_or_away == 'home':
						result = home_fixture_result
					elif home_or_away == 'away':
						result = away_fixture_result
					else:
						return 'Err'

					if result == 'W':
						output = '(*)'
					else:
						output = ''

					str_len = len(output)

					if home_or_away == 'home':
						output = output + ' ' * (indent_block_length - str_len)
					elif home_or_away == 'away':
						output = ' ' * (indent_block_length - str_len) + output
					else:
						output = ' ' * indent_block_length

					return output


				def create_score_block(home_or_away):
					if home_or_away == 'home':
						score = str(home_fixture_score)
					elif home_or_away == 'away':
						score = str(away_fixture_score)
					else:
						return 'Err'

					if len(score) < score_block_length:
						if home_or_away == 'home': 
							output = ((score_block_length - len(score)) * ' ') + score
						elif home_or_away == 'away': 
							output = score + ((score_block_length - len(score)) * ' ')
						else:
							output = ' ' * score_block_length

					return output




				line += create_indent_block('home')
				line += home_team_name
				line += ' ' * home_team_indent
				line += create_score_block('home')
				line += ' // '
				line += create_score_block('away')
				line += ' ' * away_team_indent
				line += away_team_name
				line += create_indent_block('away')

				fixture_lines_list.append(line)

			line_length = len(max(fixture_lines_list, key=len))

			div_line = '/' * line_length

			#compose file
			file_content.append(title_line)
			file_content.append(blank_line)
			file_content.append(div_line)
			file_content.append(blank_line)

			for line in fixture_lines_list:
				file_content.append(line)

			file_content.append(blank_line)
			file_content.append(div_line)


			for line in file_content:
				f.write(line + '\n')





def execute():

	global database
	database = return_load_json_file('2020_season_data.json')

	write_results()

execute()