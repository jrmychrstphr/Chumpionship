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
# Scrapes FPL league matches page for each manager #
# Returns a dict of each team's fixture opponent by gameweek #

def scrape_and_return_fixture_data():

	#grab the league's FPL code from the database
	league_code = database['league_data']['fpl_league_code']

	player_fixture_lists = {}

	#for each code in the list 'manager_codes'...
	for manager_code in return_manager_codes_as_list():

		player_fixture_lists[manager_code] = {}

		fixture_data = {}
		fpl_fixtures_page_url = "https://fantasy.premierleague.com/leagues/" + league_code + "/matches/h?entry=" + manager_code

		try:
			print("Loading fixtures page for: ", return_lookup_manager_fullname(manager_code))

			#open the manager's league matches page
			driver.get(fpl_fixtures_page_url)
			
			#wait for the fixture table to appear in DOM
			element = WebDriverWait(driver, 10).until(
				EC.presence_of_element_located((By.CSS_SELECTOR, "table.Table-ziussd-1.MatchesTable-sc-1p0h4g1-0.bPMfKH"))
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
			table_rows = soup.select("table.Table-ziussd-1.MatchesTable-sc-1p0h4g1-0.bPMfKH tbody tr")

			#scrape FPL fixture list for each team in the database
			for row in table_rows:
				item_array = row.contents

				gameweek = str("{0:0=2d}".format(int(item_array[0].get_text())))

				for x in item_array:
					if "MatchesEntry" in str(x):
						code = x.find('a').get('href').split('/')[2]
						#print(x.find('a').get('href').split('/')[2])

						# The DOM will have 2 matching hrefs for each fixture
						# The href that does not contain the current manager_code will be the opponent's code
						if code != manager_code:
							opponent_code = code

				player_fixture_lists[manager_code][gameweek] = opponent_code

	return player_fixture_lists


###############
# Adds the following to input:
# + fixture_class: Randomised Home and Away fixture class
# + opponent_manager_fullname: Full name of opponent manager
# + opponent_team_name: Name of opponent team

# Returns the result formatted as json / dict #

# Input MUST be the result of the return_scraped_fixture_data() function #
		
def compile_weekly_fixtures(input_dict):

	weekly_fixtures = {}

	for player_code, val in input_dict.items():
		for gw, opp_code in val.items():
			
			# if the gameweek is not in the dict, add it
			if gw not in weekly_fixtures:
				weekly_fixtures[gw] = []

	for gw in weekly_fixtures:

		print(gw)	
		manager_codes = return_manager_codes_as_list()
		random.shuffle(manager_codes)

		while len(manager_codes) > 0:

			team_a = manager_codes[0]
			team_b = input_dict[manager_codes[0]][gw]

			manager_codes.remove(team_a)				
			manager_codes.remove(team_b)

			fixture_obj = {}

			#check if fixture has already occurred earlier in the season
			if int(gw) > 1:
				for week, fixtures in weekly_fixtures.items():
					for fixture in fixtures:
						if (fixture['home_team'] == team_a or fixture['home_team'] == team_b) and (fixture['away_team'] == team_a or fixture['away_team'] == team_b):
							
							home_team = team_a
							away_team = team_b

						else: 
							home_team = team_b
							away_team = team_a


			fixture_obj['home_team'] = team_b
			fixture_obj['away_team'] = team_a

			weekly_fixtures[gw].append(fixture_obj)

			continue

	return weekly_fixtures

compile_player_fixtures()


###############
# Pushes 'fixture_list' to database
def push_fixtures_to_database(fixtures):
	database['fixture_list'] = fixtures

###############
# write data to json file
def write_to_json_file(filename, input_data):
    with open(filename+'.json', 'w') as json_file:
        json.dump(input_data, json_file, sort_keys=True, indent=4, separators=(',', ': '))

def return_create_date_stamp():
	now = datetime.datetime.now()

	year = now.strftime("%Y")
	month = now.strftime("%m")
	day = now.strftime("%d")
	hour = now.strftime("%H")
	minute = now.strftime("%M")

	datestamp = year + month + day + "_" + hour + minute
	return datestamp






##############
def execute(): 

	global database
	database = return_load_json_file('_versions/chumpionship_2021_database-new-history.json')

	open_browser()

	push_fixtures_to_database(compile_weekly_fixtures(scrape_and_return_fixture_data()))
	
	close_browser()
	
	write_to_json_file('_versions/chumpionship_2021_database---'+return_create_date_stamp(), database)


execute()