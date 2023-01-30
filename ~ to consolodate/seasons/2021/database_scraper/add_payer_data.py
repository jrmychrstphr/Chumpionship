import json
from pathlib import Path
import datetime


###############
# Loads a .json file from the same directory as this script file #
# returns the result  #

def return_load_json_file(filename):

	print("loading file... ", filename)

	try:
		f = open(filename + '.json')
		json_data = json.load(f)
		f.close()

	except:
		print("Error: Failed to load file")
	else:
		print("Success!")
		return json_data


###############
# write data to json file
def write_to_json_file(filename, input_data):
    with open(filename + '.json', 'w') as json_file:
        json.dump(input_data, json_file, sort_keys=True, indent=4, separators=(',', ': '))

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



def return_create_date_stamp():
	now = datetime.datetime.now()

	year = now.strftime("%Y")
	month = now.strftime("%m")
	day = now.strftime("%d")
	hour = now.strftime("%H")
	minute = now.strftime("%M")

	datestamp = year + month + day + "_" + hour + minute
	return datestamp



def execute():

	#load the clean database file
	global database
	database = return_load_json_file('_versions/chumpionship_2021_database---new')

	for manager_code in return_manager_codes_as_list():
		database['player_data'][manager_code]['gw_performance'] = {}
		database['player_data'][manager_code]['fixtures'] = {}


	for gameweek, fixture_list in database['fixture_list'].items():
		for val in fixture_list:
			#home team
			database['player_data'][val['home_team']]['fixtures'][gameweek] = {}
			database['player_data'][val['home_team']]['fixtures'][gameweek]['opponent_code'] = val['away_team']
			database['player_data'][val['home_team']]['fixtures'][gameweek]['class'] = 'home'

			#away team
			database['player_data'][val['away_team']]['fixtures'][gameweek] = {}
			database['player_data'][val['away_team']]['fixtures'][gameweek]['opponent_code'] = val['home_team']
			database['player_data'][val['away_team']]['fixtures'][gameweek]['class'] = 'away'


	#save a version in the version folder
	datestamp = return_create_date_stamp()
	write_to_json_file('_versions/chumpionship_2021_database---' + datestamp, database)

	#print(database)

execute()