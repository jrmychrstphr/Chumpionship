import json
from pathlib import Path
import datetime

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
		f = open(filename + '.json')
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


###############
# scrapes

def scrape_gw_performance_data():

	for manager_code in return_manager_codes_as_list():

		# Build the url
		transfers_url = "https://fantasy.premierleague.com/entry/"+manager_code+"/transfers"

		try:
			#open the page
			driver.get(transfers_url)
			
			#wait for the gameweek-by-gameweek data table container to appear
			WebDriverWait(driver, 5).until(
				EC.presence_of_element_located((By.CSS_SELECTOR, ".Table-ziussd-1.fVnGhl"))
			)


		except:
			#if the table is *not* found...
			try:
				#Look for the page placeholder instead
				element = WebDriverWait(driver, 5).until(
					EC.text_to_be_present_in_element((By.CSS_SELECTOR, ".Layout__Main-eg6k6r-1"), "No transfers have been made yet for this team.")
				)

			except:
				print("Err – unable to scrape transfer data")
			else:
				transfers_obj = False
		
		else:
			#if the table is found...

			transfers_obj = {}

			transfers_page_soup = BeautifulSoup(driver.page_source, 'lxml')

			#locate 'This Season' table
			transfers_history = transfers_page_soup.find("h2", text="Transfers")

			#move up the soup DOM until a table is found
			while len(transfers_history.select('.Table-ziussd-1.fVnGhl')) == 0:
				transfers_history = transfers_history.parent
			else:
				transfers_history = transfers_history

			transfers_history_table_rows = transfers_history.select('.Table-ziussd-1.fVnGhl tbody tr')

			for row in transfers_history_table_rows:

				row_contents_array = row.contents
				gameweek = str("{0:0=2d}".format(int(row_contents_array[3].get_text().lower().replace('gw', ''))))

				if gameweek not in transfers_obj:
					transfers_obj[gameweek] = 1
				else:
					transfers_obj[gameweek] = transfers_obj[gameweek] + 1

		print(transfers_obj)





def execute():

	#load the clean database file
	global database
	database = return_load_json_file('../database/_versions/chumpionship_2021_database---new')

	open_browser()

	scrape_gw_performance_data()

	close_browser()

execute()