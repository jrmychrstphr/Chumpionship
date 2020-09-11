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
		f = open(filename)
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


##############
# Scrapes pervious season scores #
# stores them to player_data > fpl_history #
def scrape_and_return_fpl_history(manager_code):

	manager_URL = 'https://fantasy.premierleague.com/entry/'+manager_code+'/history'

	try:
		#open the webpage
		driver.get(manager_URL)
		
		#wait for the league table to appear in DOM
		element = WebDriverWait(driver, 10).until(
			EC.presence_of_element_located((By.CSS_SELECTOR, "table.Table-ziussd-1.fVnGhl"))
		)
		
	except:
		#if the table is not found, display an error message
		print("Error: Table element not found :(")
	
	else:
		#if the table is found, display successs message
		print("Success: Table element found :D")

		#create soup of page DOM
		soup = BeautifulSoup(driver.page_source, 'lxml')

		#locate 'Previous seasons' table
		element = soup.find("h3", text="Previous Seasons")

		#move up the soup DOM until the table is found
		while len(element.select('.Table-ziussd-1.fVnGhl')) == 0:
			element = element.parent
		else:
			prev_seasons_rows = element.select('.Table-ziussd-1.fVnGhl tbody tr')

			fpl_history = {}

			for row in prev_seasons_rows:
				row_contents_array = row.contents

				season = row_contents_array[0].get_text().replace("/", "_")
				score = row_contents_array[1].get_text()

				fpl_history[season] = score

			return fpl_history


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

	global database
	database = return_load_json_file('chumpionship_2021_database - new.json')

	open_browser()


	for manager_code in return_manager_codes_as_list():
		database['player_data'][manager_code]['manager_info']['fpl_history'] = scrape_and_return_fpl_history(manager_code)

	close_browser()

	write_to_json_file('chumpionship_2021_database---history', database)

execute()