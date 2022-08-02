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
# scrapes performance data for  #
def return_scrape_transfer_data():

	manager_code_list = return_manager_codes_as_list()

	#declare dict to store data in 
	transfer_data = {}


	for manager_code in manager_code_list:

		#declare dict to store data in 
		scraped_data = {}

		# Build the url
		#url = "https://fantasy.premierleague.com/entry/"+manager_code+"/event/"+gameweek
		url = "https://fantasy.premierleague.com/entry/"+manager_code+"/transfers"

		try:
			print("Loading transfers page for: ", manager_code)

			#open the page
			driver.get(url)
			
			#wait for the gameweek-by-gameweek data table container to appear
			element = WebDriverWait(driver, 10).until(
				EC.presence_of_element_located((By.CSS_SELECTOR, "table.Table-ziussd-1.fVnGhl tbody tr"))
			)


		except:
			#if the table is not found, display an error message
			print("Error: Data table not found")
		
		else:
			print("Success! Let's scrape some transfer data")

			#create soup of DOM
			soup = BeautifulSoup(driver.page_source, 'lxml')

			#locate Transfers title
			element = soup.find("h2", text="Transfers")

			#move up the soup DOM until the table is found
			while len(element.select('.Table-ziussd-1.fVnGhl')) == 0:
				element = element.parent
			else:
				table_rows = element.select('.Table-ziussd-1.fVnGhl tbody tr')

			#print(table_rows)

			for row in table_rows:

				print (row)

				row_contents_array = row.contents
				row_gameweek_string = row_contents_array[3].get_text()
				gw = str("{0:0=2d}".format(int(row_gameweek_string.lower().replace('gw', ''))))

				#print(row_gameweek_string.lower().replace('gw', ''))

				# if the gameweek is not in the scraped data dict, 
				# add the gameweek to the dict and set the val to 1

				if gw not in scraped_data:
					scraped_data[gw] = 1
				# else, +1 to the value
				else:
					scraped_data[gw] = scraped_data[gw]+1


		transfer_data[manager_code] = scraped_data

	# push transfers made to performance data
	for manager_code in manager_code_list:

		print(manager_code)
		perf = database['player_data'][manager_code]['gw_performance']

		for key, val in perf.items():

			if key not in transfer_data[manager_code]:
				transfers_made = 0

			else:
				transfers_made = transfer_data[manager_code][key]

			print( 'Transfers in gw' + str(key) + ': ' + str(transfers_made))
			database['player_data'][manager_code]['gw_performance'][key]['transfers_made'] = transfers_made

	print(database)




def push_to_database_gw_performance_data(input_data):

	for key, val in input_data.items():

		manager_code = key
		performance_data = val

		database['player_data'][manager_code]['gw_performance'] = val



###############
# write data to json file
def write_to_json_file(filename, input_data):
    with open(filename + '.json', 'w') as json_file:
        json.dump(input_data, json_file, sort_keys=True, indent=4, separators=(',', ': '))



def push_to_database_season_performance_data(input_data):

	for key, val in input_data.items():

		manager_code = key

		database['player_data'][manager_code]['season_performance'] = val


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
	database = return_load_json_file('2020_season_data - u.json')

	open_browser()


	#print(database)
	#write_to_json_file('2020_season_data - u', database)

	return_scrape_transfer_data()

	close_browser()

execute()