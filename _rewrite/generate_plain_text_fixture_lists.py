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



def return_team_names_as_list():

	team_names = []

	#create a list contaiing the FPL code of every manager in the database
	for key, val in database['player_data'].items():

		team_name = val['manager_info']['team_name']
		team_names.append(team_name)

	return team_names



def write_fixture_list(gw_data):

	gameweek = gw_data[0]
	fixture_list = gw_data[1]

	# define the name for the file
	filename = 'plain_text_assets/' + gameweek + '---fixtures.txt'

	# create a new .txt file
	f = open(filename,'w+')

	# declare an array / list to store 
	# line-by-line content to write to the file
	file_content = []

	# create file title line
	title_line = 'Chumpionship 2020 - GW' + gameweek + ' fixtures'
	blank_line = ''


	#declare size of fixture line blocks:

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

	for fixture in fixture_list:

		line = ''

		home_team_name = fixture['H']['team_name']
		home_team_indent = team_name_block - len(home_team_name)

		away_team_name = fixture['A']['team_name']
		away_team_indent = team_name_block - len(away_team_name)

		line += ' ' * indent_block_length
		line += home_team_name
		line += ' ' * home_team_indent
		line += ' ' * score_block_length
		line += ' // '
		line += ' ' * score_block_length
		line += ' ' * away_team_indent
		line += away_team_name
		line += ' ' * indent_block_length

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

	for x in database['fixture_list'].items():
		write_fixture_list(x)

execute()