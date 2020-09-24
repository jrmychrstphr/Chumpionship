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
		url = "https://fantasy.premierleague.com/entry/"+manager_code+"/history"

		try:
			print("Loading season history page for ", manager_code )

			#open the page
			driver.get(url)
			
			#wait for the gameweek-by-gameweek data table container to appear
			element = WebDriverWait(driver, 10).until(
				EC.presence_of_element_located((By.CSS_SELECTOR, ".Table__ScrollTable-ziussd-0.canFyp"))
			)


		except:
			#if the table is not found, display an error message
			print("Error - Data table not found")
		
		else:
			print("Success! Lets scrape some data")

			#create soup of DOM
			soup = BeautifulSoup(driver.page_source, 'lxml')

			#locate 'This Season' table
			element = soup.find("h3", text="This Season")

			#move up the soup DOM until the table is found
			while len(element.select('.Table-ziussd-1.fVnGhl')) == 0:
				element = element.parent
			else:
				anchors = element.find_all('a')

				for anchor in anchors:

					#return_lookup_manager_fullname(manager_code)
					#"/entry/1266186/event/1"

					href = anchor.get('href')
					gameweek = href.split('/')[4]

					try:
						print("Loading GW", gameweek, "for", return_lookup_manager_fullname(manager_code))

						#open each GW href in the table
						driver.get("https://fantasy.premierleague.com" + href)

						#wait for the gameweek-by-gameweek data table container to appear
						WebDriverWait(driver, 10).until(
							EC.presence_of_element_located((By.CSS_SELECTOR, "a.Tab__Link-sc-19t48gi-1.dSNXUO"))
						)

					except:
						print("Page failed to load")
					else:
						print("Page loaded")

						#"Click" the list view toggle to reveal the data table
						driver.find_element_by_link_text('List View').click()
						print("Button clicked")


						try:
							print("Waiting for data tables to appear...")

							#wait for the gameweek-by-gameweek data table container to appear
							WebDriverWait(driver, 10).until(
								EC.presence_of_element_located((By.CSS_SELECTOR, ".sc-AykKC.fbHWCH table.Table-ziussd-1.EntryEventTable__StatsTable-sc-1d2xgo1-1.dbevix"))
							)

						except:
							print("Table failed to appear")
						else:

							print("Table found")

							#create a new soup of DOM
							soup = BeautifulSoup(driver.page_source, 'lxml')

							player_data_tables = soup.select(".sc-AykKC.fbHWCH table.Table-ziussd-1.EntryEventTable__StatsTable-sc-1d2xgo1-1.dbevix")
							#print(player_data_tables)

							for idx, table in enumerate(player_data_tables):

								if idx == 0: 
									squad_status = "on field"
								elif idx == 1:
									squad_status = "on bench"

								table_rows = table.select("tbody tr")
								for row in table_rows:
									row_cells = row.select("td")

									#row_cells[0] # information button
									#row_cells[1] # Captain / VC icon
									if len(row_cells[1].select("svg.TableCaptains__StyledCaptain-sc-1ub910p-0")) > 0:
										print("* Captain *")
									elif len(row_cells[1].select("svg.TableCaptains__StyledViceCaptain-sc-1ub910p-1")) > 0:
										print("* Vice Captain *")

									#row_cells[2] # Name / Team / Position info
									player_information_container = row_cells[2].select("div.Media__Body-sc-94ghy9-2")

									player_name = player_information_container[0].select(".ElementInTable__Name-y9xi40-1")[0].get_text()
									player_team = player_information_container[0].select(".ElementInTable__Team-y9xi40-2")[0].get_text()
									player_position = player_information_container[0].select(".ElementInTable__Team-y9xi40-2")[0].parent.contents[1].get_text()

									print(player_name)
									print(player_team)
									print(player_position)

									#row_cells[3] # Points scored
									points_scored = row_cells[3].get_text()

									#row_cells[4] # Minutes played
									#row_cells[5] # Goals scored
									#row_cells[6] # Assists
									#row_cells[7] # Clean sheets
									#row_cells[8] # Goals conceded
									#row_cells[9] # Own goals
									#row_cells[10] # Penalties saved
									#row_cells[11] # Penalties missed
									#row_cells[12] # Yellow cards
									#row_cells[13] # Red Cards
									#row_cells[14] # Saves
									#row_cells[15] # Bonus points
									#row_cells[16] # Bonus system score
									#row_cells[17] # Influence score (I)
									#row_cells[18] # Creativity score (C)
									#row_cells[19] # Threat score (T)
									#row_cells[20] # ITC index

									print("")


def execute():

	#load the clean database file
	global database
	database = return_load_json_file('../database/_versions/chumpionship_2021_database---new')

	open_browser()

	scrape_gw_performance_data()

	close_browser()

execute()