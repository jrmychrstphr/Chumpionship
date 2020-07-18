import json
from pathlib import Path

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import operator
import random



###############
# Opens a Firefox webdriver #
# sets gloabl var 'driver' #

def open_browser():
	# Open browser
	global driver
	driver = webdriver.Firefox()
	print("Browser opened")

	
###############
# Closes browser #

def close_browser():
	#close browser
	driver.quit()
	print("Browser closed")


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


###############
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



###############
# Scans 'player_data' in the database #
# Counts the number of values stored in 'fixtures' to define a season length #
# Returns the season leangth IF all lengths are the same  #

# Database MUST have fixtures defined before calling this function  #

def return_count_fixtures():

	fixtures_count = []

	manager_codes = return_manager_codes_as_list()
	
	#create a list contaiing the FPL code of every manager in the database
	for key, val in database['player_data'].items():

		player_idx = key
		player_data = val

		fixtures_count.append(len(val['fixtures']))

	def all_same(items):
		return all(x == items[0] for x in items)

	if all_same(fixtures_count):
		#print('Gameweeks: ', fixtures_count[0])
		return  fixtures_count[0]
	else:
		print('Error: Inconsistent season lengths')


###############
# Scrapes FPL league matches page for each manager #
# Returns the resulting dictionary / json #

def return_scraped_fixture_data():

	#grab the league's FPL code from the database
	league_code = database['league_data']['fpl_league_code']

	#declare a list to hold manager codes
	manager_codes = return_manager_codes_as_list()

	#declare a dict to hold fixture information
	output_dict = {}

	#for each code in the list 'manager_codes'...
	for manager_code in manager_codes:


		output_dict[manager_code] = {}
		fpl_fixtures_page_url = "https://fantasy.premierleague.com/leagues/" + league_code + "/matches/h?entry=" + manager_code

		try:
			print("Loading match page for: ", return_lookup_team_name(manager_code))

			#open the manager's league matches page
			driver.get(fpl_fixtures_page_url)
			
			#wait for the fixture table to appear in DOM
			element = WebDriverWait(driver, 10).until(
				EC.presence_of_element_located((By.CSS_SELECTOR, "table.MatchesTable-sc-1p0h4g1-0"))
			)
			
		except:
			#if the table is not found, display an error message
			print("Error: League table element not found")
		
		else:
			#if the table is found, display successs message
			print("Success!")

			#create soup of DOM
			soup = BeautifulSoup(driver.page_source, 'lxml')

			#filter to the tr elements wirth fixtures
			table_rows = soup.select("table.MatchesTable-sc-1p0h4g1-0 tbody tr")

			#scrape FPL fixture list for each team in the database
			for item in table_rows:
				item_array = item.contents

				fixture_gameweek = str("{0:0=2d}".format(int(item_array[0].get_text())))

				for x in item_array:
					if "MatchesEntry" in str(x):
						code = x.find('a').get('href').split('/')[2]
						#print(x.find('a').get('href').split('/')[2])

						# The DOM will have 2 matching hrefs for each fixture
						# The href that does not contain the current manager_code will be the opponent's code
						if code != manager_code:
							opponent_code = code

				output_dict[manager_code][fixture_gameweek] = {}
				output_dict[manager_code][fixture_gameweek]['opponent_manager_fpl_code'] = opponent_code

	return(output_dict)



###############
# Adds the following to input:
# + fixture_class: Randomised Home and Away fixture class
# + opponent_manager_fullname: Full name of opponent manager
# + opponent_team_name: Name of opponent team

# Returns the result formatted as json / dict #

# Input MUST be the result of the return_scraped_fixture_data() function #
		
def return_generate_fixture_information(input_dict):

	def update_prev_fix_dict(opponent_code, fixture_class):
		prev_fix_class_dict[opponent_code] = fixture_class

	def check_prev_fix_exists(opponent_code):
		if opponent_code in prev_fix_class_dict:
			return True
		else:
			return False

	def return_prev_fix_class(opponent_code):
		if opponent_code in prev_fix_class_dict:
			return prev_fix_class_dict[opponent_code]
		else:
			print("Error: Fixture Class for previous fixture not found!")


	def return_alternate_fix_class(input_class):
		if input_class == 'H' or input_class == 0:
			return 'A'
		elif input_class == 'A' or input_class == 1:
			return 'H'
		else:
			print("Error: Unable to process input fixture_class")

	def return_fix_class(input_binary):
		if input_binary == 0:
			return 'H'
		elif input_binary == 1:
			return 'A'
		else:
			print('Error: input_binary was not 0 or 1')


	#for each 'player' (top-level item) in the data
	for key_1, val_1 in input_dict.items():

		#print('key_1: ',key_1)
		#print('val_1: ',val_1)

		#declare a blank dict to hold prev_fix info (prev_fix)
		prev_fix_class_dict = {}

		#for each gw (lv.2 items in heirachy) of season (as defined by FPL scrape)
		for key_2, val_2 in val_1.items():

			#print('key_2: ',key_2)
			#print('val_2: ',val_2)

			opponent_code = val_2['opponent_manager_fpl_code']

			#add opponent_manager_fullname
			val_2['opponent_manager_fullname'] = return_lookup_manager_fullname(opponent_code)
			#add opponent_teamname
			val_2['opponent_team_name'] = return_lookup_team_name(opponent_code)

			#generate fixture_class:
			
			#if a fixture exists
			if 'fixture_class' in val_2:

				#update the prev_fix list with new fixture_class
				fixture_class = val_2['fixture_class']
				update_prev_fix_dict(opponent_code, fixture_class)

			#if a fixture does not exist
			else:

				#check prev_fix list if opponent has been played before
				
				#if oppontent HAS been played before
				if check_prev_fix_exists(opponent_code):

					#set fixture_class as alternate to prev_fix
					val_2['fixture_class'] = return_alternate_fix_class(return_prev_fix_class(opponent_code))
					
					#update prev_fix list
					update_prev_fix_dict(opponent_code, val_2['fixture_class'])

				#if opponent HAS NOT played
				else:
					#randomise a fixture_class
					random_fixture_class = return_fix_class(random.randint(0, 1))

					#set fixture_class to the random class
					val_2['fixture_class'] = random_fixture_class

					#update prev_fix list
					update_prev_fix_dict(opponent_code, val_2['fixture_class'])

			#assign the opposite fixture_class to opponent:

			opp_fixture = input_dict[opponent_code][key_2]

			#check if opponent has fixture class set
			if 'fixture_class' not in opp_fixture:
				opp_fixture['fixture_class'] = return_alternate_fix_class(val_2['fixture_class'])

	#print(input_dict)
	return input_dict


###############
# Push dict / json to database #

def push_fixtures_to_player_data(input_data):
	
	for key, val in input_data.items():

		#print('key: ',key)
		#print('val: ',val)

		player_code = key
		fixture_data = val

		if database:

			# cycle through database
			for key, val in database['player_data'].items():


				if val['manager_info']['fpl_code'] == player_code:
					val['fixtures'] = fixture_data
					
		else:
			print('Error: unable to access database')


	#print(database)

###############
# Executes the functions in correct order needed to: #
# + Scrape fixture data from the FPL league page #
# + Add fixture info (e.g. Home and Away) #
# + Push the result to the database variable #

def execute_add_fixtures_to_player_data():
	scraped_fixture_data = return_scraped_fixture_data()
	generated_fixture_data = return_generate_fixture_information(scraped_fixture_data)
	push_fixtures_to_player_data(generated_fixture_data)



###############
# Compiles a gameweek-by-gameweek fixtures list #
# Based on fixture info stroed within 'player_data' for each manager #
# Returns a dict with this in

# MUST be called AFTER fixture data is added to 'player_data' #

def return_compile_fixture_list():

	def return_fixture_data(manager_code, gameweek):

		for key, val in database['player_data'].items():

			if val['manager_info']['fpl_code'] == manager_code:
				gw = str("{0:0=2d}".format(int(gameweek)))
				fixture_data = val['fixtures'][gw]
				return fixture_data


	#declare a dict to store fixture in
	fixtures = {}

	#for each gameweek
	for x in range(return_count_fixtures()):

		#create a fresh list of all manager flp codes
		manager_code_list = return_manager_codes_as_list()
		
		#define the gameweek
		gw = str("{0:0=2d}".format(int(x)+1))

		#declare empty dict to store this gw's fixtures
		gameweek_fixtures = []

		#cycle through the list of codes
		while len(manager_code_list) > 0:
			
			manager_code = manager_code_list[0]

			manager_team_name = return_lookup_team_name(manager_code)
			
			#look up that manager's fixture in this gw
			fixture_data = return_fixture_data(manager_code, gw)

			opp_code = fixture_data['opponent_manager_fpl_code']
			opp_team_name = fixture_data['opponent_team_name']
			fixture_class = fixture_data['fixture_class']

			#push this to a dict with home team, away team
			fix = {}

			if fixture_class == 'H':
				fix_home_team_name = manager_team_name
				fix_home_code = manager_code

				fix_away_team_name = opp_team_name
				fix_away_code = opp_code

			elif fixture_class == 'A':
				fix_home_team_name = opp_team_name
				fix_home_code = opp_code

				fix_away_team_name = manager_team_name
				fix_away_code = manager_code
			else:
				print('Error!')

			fix['H'] = {}
			fix['A'] = {}

			fix['H']['team_name'] = fix_home_team_name
			fix['H']['manager_code'] = fix_home_code

			fix['A']['team_name'] = fix_away_team_name
			fix['A']['manager_code'] = fix_away_code

			#remove both team codes from list
			manager_code_list.remove(manager_code)
			manager_code_list.remove(opp_code)

			gameweek_fixtures.append(fix)

		sorted_gameweek_fixtures = sorted(gameweek_fixtures, key=lambda k: k['H']['team_name']) 

		fixtures[gw] = sorted_gameweek_fixtures


	return fixtures


###############
# Pushes 'fixture_list' to database
def push_fixtures_to_database(fixtures):
	database['fixture_list'] = fixtures

###############
# Executes the functions in correct order needed to: #
# + Compile a dict of gameweek-by-gameweek fixtures #
# + Push the result to the database variable #
def execute_add_fixture_list():
	fixtures = return_compile_fixture_list()
	push_fixtures_to_database(fixtures)


###############
# write data to json file
def write_to_json_file(filename, input_data):
    with open(filename + '.json', 'w') as json_file:
        json.dump(input_data, json_file, sort_keys=True, indent=4, separators=(',', ': '))




##############
def execute(): 

	global database
	database = return_load_json_file('Mean-Goals_season_data - new.json')

	open_browser()

	execute_add_fixtures_to_player_data()
	execute_add_fixture_list()
	
	close_browser()

	print(database)
	
	write_to_json_file('2020_season_data - u', database)


execute()