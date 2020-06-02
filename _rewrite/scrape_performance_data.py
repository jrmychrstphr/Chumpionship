import json
from pathlib import Path

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



###############
# Open browser #

def open_browser():
	# Open browser
	global driver
	driver = webdriver.Firefox()
	print("Browser opened")

	
###############
# Close browser #

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
# scrapes performance data for  #
def return_lookup_opponent_code(manager_code, gameweek):

	for key, val in database['player_data'].items():

		if val['manager_info']['fpl_code'] == manager_code:
			opponent_code = val['fixtures'][gameweek]['opponent_manager_fpl_code']
			return opponent_code


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
# scrapes performance data for  #
def scrape_performance_data(manager_code):

	# if database already contains gw data
	if 'gw_performance' in database['player_data'][manager_code]:

		# ask user if existing data should be replaced
		print('Database contains existing gw_performance data')
		user_input = input('Update existing data? (Y/N): ')

		if str(user_input.upper()) == "Y":
			update_data = True
		else:
			update_data = False
	else:
		print('database does not contain existing gw_performance data')


	#declare dict to store data in 
	scraped_data = {}

	# Build the url
	#url = "https://fantasy.premierleague.com/entry/"+manager_code+"/event/"+gameweek
	url = "https://fantasy.premierleague.com/entry/"+manager_code+"/history"

	try:
		print("Loading page for: ", manager_code)

		#open the page
		driver.get(url)
		
		#wait for the gameweek-by-gameweek data table container to appear
		element = WebDriverWait(driver, 10).until(
			EC.presence_of_element_located((By.CSS_SELECTOR, ".Table__ScrollTable-ziussd-0.canFyp"))
		)


	except:
		#if the table is not found, display an error message
		print("Error: Data table not found")
	
	else:
		print("Success! Let's scrape some data")

		#create soup of DOM
		soup = BeautifulSoup(driver.page_source, 'lxml')

		#filter to gw_performance table
		season_table_rows = soup.select(".Table__ScrollTable-ziussd-0.canFyp table tbody tr")

		for row in season_table_rows:

			row_contents_array = row.contents

			row_gameweek = row_contents_array[0].find('a').get('href').split('/')[4]


			points_scored = float(row_contents_array[1].get_text())
			points_on_bench = float(row_contents_array[2].get_text())
			transfers_made = float(row_contents_array[4].get_text())
			points_spent = float(row_contents_array[5].get_text())
			overall_total_points = float(row_contents_array[6].get_text())
			squad_value = float(row_contents_array[8].get_text())

			fixture_score = points_scored - points_spent

			gw = str("{0:0=2d}".format(int(row_gameweek)))

			if gw not in scraped_data:

				scraped_data[gw] = {}

			scraped_data[gw]['points_scored'] = points_scored
			scraped_data[gw]['points_spent'] = points_spent
			scraped_data[gw]['fixture_score'] = fixture_score
			scraped_data[gw]['transfers_made'] = transfers_made
			scraped_data[gw]['squad_value'] = squad_value
			scraped_data[gw]['overall_total_points'] = overall_total_points

			fixture_opponent_manager_code = return_lookup_opponent_code(manager_code, gw)
			fixture_opponent_team_name = return_lookup_team_name(fixture_opponent_manager_code)
			fixture_opponent_manager_fullname = return_lookup_manager_fullname(fixture_opponent_manager_code)
			
			scraped_data[gw]['fixture_opponent_manager_code'] = fixture_opponent_manager_code
			scraped_data[gw]['fixture_opponent_team_name'] = fixture_opponent_team_name
			scraped_data[gw]['fixture_opponent_manager_fullname'] = fixture_opponent_manager_fullname


		print(scraped_data)

		#locate Chips played table
		element = soup.find("h3", text="Chips")

		#move up the soup DOM until the table is found
		while len(element.select('.Table-ziussd-1.fVnGhl')) == 0:
			element = element.parent
		else:
			chips_played_table_rows = element.select('.Table-ziussd-1.fVnGhl tbody tr')

		chips_played = {}

		for row in chips_played_table_rows:


			row_contents_array = row.contents

			chip_name = row_contents_array[1].get_text()
			chip_gameweek = row_contents_array[2].find('a').get('href').split('/')[4]

			chip_gw = str("{0:0=2d}".format(int(chip_gameweek)))

			chips_played[chip_gw] = chip_name

		print(chips_played)

		#cycle through scraped data and add the chips
		for key, val in scraped_data.items():

			print(key)
			print(scraped_data[key])

			if key in chips_played:
				print('Chip played in gw', key, ': ', chips_played[key])
				chip = chips_played[key]
			else:
				chip = 'None'


			scraped_data[key]['chip_played'] = chip

		print(scraped_data)





def execute():
	global database
	database = return_load_json_file('2020_season_data.json')

	open_browser()

	scrape_performance_data('75107')

	close_browser()

execute()
