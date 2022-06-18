from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pathlib import Path
import os
import json

from bs4 import BeautifulSoup


###############
# Open browser #

def open_browser():
	global driver
	driver = webdriver.Firefox()
	print("Browser opened")

	
###############
# Close browser #

def close_browser():
	driver.quit()
	print("Browser closed")


def scrape():

	database_dir = './database'

	for dirpath, dirnames, files in os.walk(database_dir):
		print(f'Found directory: {dirpath}')

		if not dirpath == database_dir:

			existing_gameweeks = []
			#player_code

			for file_name in files:

				#print(file_name)

				# open player_info.json
				if file_name == 'player_info.json':
					# get manager code from player_info.json
					with open(dirpath + "/" + file_name) as f:
						d = json.load(f)
						manager_code = d['manager_code']
						#print(manager_code)

				# populate list of existing gameweeks
				elif file_name.startswith('GW'):

					gameweek = file_name.replace("GW", "").replace(".json", "")
					existing_gameweeks.append(gameweek)

			# print(existing_gameweeks)


			# Build the url
			url = "https://fantasy.premierleague.com/entry/"+manager_code+"/history"

			try:
				print("Loading season history page...")

				#open the page
				driver.get(url)

				#wait for the gameweek-by-gameweek data table container to appear
				WebDriverWait(driver, 5).until(
				EC.presence_of_element_located((By.CSS_SELECTOR, ".Table__ScrollTable-ziussd-0.itIXYu"))
				)

			except:
				#if the table is not found, display an error message
				print("Error - Data table not found")

			else:
				print("Success!")

				data_dict = {}

				# create soup of DOM
				history_page_soup = BeautifulSoup(driver.page_source, 'lxml')

				#locate 'This Season' table
				season_history_data_table = history_page_soup.find("h3", text="This Season")

				# move up the soup DOM until the table is found
				while len(season_history_data_table.select('.Table-ziussd-1.fHBHIK')) == 0:
					season_history_data_table = season_history_data_table.parent
				
				else:
					season_history_data_table = season_history_data_table
					season_history_table_rows = season_history_data_table.select('.Table-ziussd-1.fHBHIK tbody tr')

				for row in season_history_table_rows:

					# scrape data
					row_contents_array = row.contents
					gameweek = row_contents_array[0].find('a').get('href').split('/')[4]

					# gameweek (e.g. 01, 02, ...)
					gameweek = str("{0:0=2d}".format(int(gameweek)))

					if gameweek not in existing_gameweeks:

						points_scored = int(float(row_contents_array[1].get_text()))
						points_on_bench = int(float(row_contents_array[2].get_text()))
						points_spent = int(float(row_contents_array[5].get_text()))
						overall_total_points = int(float(row_contents_array[6].get_text()))
						squad_value = float(row_contents_array[8].get_text())

						fixture_score = int(int(points_scored) - int(points_spent))

						# push data to data_dict
						data_dict[gameweek] = {}
						
						data_dict[gameweek]['points_scored'] = points_scored
						data_dict[gameweek]['points_on_bench'] = points_on_bench
						data_dict[gameweek]['points_spent'] = points_spent
						data_dict[gameweek]['fixture_score'] = fixture_score
						data_dict[gameweek]['squad_value'] = squad_value
						data_dict[gameweek]['overall_total_points'] = overall_total_points

						data_dict[gameweek]['chip_played'] = "None"

						data_dict[gameweek]['transfers_made'] = 0
						data_dict[gameweek]['transfered_in'] = []
						data_dict[gameweek]['transfered_out'] = []

						data_dict[gameweek]['squad'] = []


				
				##### CHIPS #####

				#locate Chips table
				chips_history_table = history_page_soup.find("h3", text="Chips")

				#move up the soup DOM until the table is found
				while len(chips_history_table.select('.Table-ziussd-1.fHBHIK')) == 0:
					chips_history_table = chips_history_table.parent
				else:
					chips_history_table_rows = chips_history_table.select('.Table-ziussd-1.fHBHIK tbody tr')

				chips_played = {}

				if len(chips_history_table_rows) > 0:

					for row in chips_history_table_rows:

						row_contents_array = row.contents

						chip_gameweek = row_contents_array[2].find('a').get('href').split('/')[4]
						chip_gameweek = str("{0:0=2d}".format(int(chip_gameweek)))

						if chip_gameweek not in existing_gameweeks:
							# push data to data_dict
							chip_name = row_contents_array[1].get_text()
							data_dict[chip_gameweek]['chip_played'] = chip_name



				##### TRANSFERS #####

				# Build the url
				transfers_url = "https://fantasy.premierleague.com/entry/"+manager_code+"/transfers"

				try:
					print("Loading transfer history page...")

					#open the page
					driver.get(transfers_url)

					#wait for the gameweek-by-gameweek data table container to appear
					WebDriverWait(driver, 5).until(
					EC.presence_of_element_located((By.CSS_SELECTOR, ".Table-ziussd-1.fHBHIK"))
					)


				except:
					#if the table is *not* found...
					try:
						#Look for the page placeholder instead
						element = WebDriverWait(driver, 5).until(
						EC.text_to_be_present_in_element((By.CSS_SELECTOR, ".Layout__Main-eg6k6r-1.wXYnc"), "No transfers have been made yet for this team.")
						)

					except:
						print("Err – No transfers")
					else:
						transfers_obj = False

				else:
					#if the table is found...
					print("Success!")

					transfers_page_soup = BeautifulSoup(driver.page_source, 'lxml')

					#locate 'This Season' table
					transfers_history_table = transfers_page_soup.find("h2", text="Transfers")

					#move up the soup DOM until a table is found
					while len(transfers_history_table.select('.Table-ziussd-1.fHBHIK')) == 0:
						transfers_history_table = transfers_history_table.parent
					else:
						transfers_history_table = transfers_history_table

					transfers_history_table_rows = transfers_history_table.select('.Table-ziussd-1.fHBHIK tbody tr')

					for row in transfers_history_table_rows:

						row_contents_array = row.contents

						# define gameweek
						transfers_gameweek = str("{0:0=2d}".format(int(row_contents_array[3].get_text().lower().replace('gw', ''))))

						if transfers_gameweek not in existing_gameweeks:

							# add 1 to the total transfers made in that gamweek
							data_dict[transfers_gameweek]['transfers_made'] += 1

							transfered_in = row_contents_array[1].get_text()
							transfered_out = row_contents_array[2].get_text()

							data_dict[transfers_gameweek]['transfered_in'].append(transfered_in)
							data_dict[transfers_gameweek]['transfered_out'].append(transfered_out)

				
				##### SQUAD #####
				gameweek_anchors = season_history_data_table.find_all('a')

				for anchor in gameweek_anchors:

					href = anchor.get('href')
					squad_gameweek = str("{0:0=2d}".format(int(href.split('/')[4])))

					if squad_gameweek not in existing_gameweeks:

						try:
							print("Loading GW", squad_gameweek)

							driver.get("https://fantasy.premierleague.com" + href)

							#wait for the data table container to appear
							WebDriverWait(driver, 5).until(
							EC.presence_of_element_located((By.CSS_SELECTOR, "a.Tab__Link-sc-19t48gi-1.dDKNAk"))
							)

						except:
							print("Page failed to load")
						else:
							print("Page loaded")

							# "Click" the list view toggle to reveal the data table
							driver.find_element_by_link_text('List View').click()
							print("Button clicked")

							try:
								print("Waiting for data tables to appear...")

								#wait for the gameweek-by-gameweek data table container to appear
								WebDriverWait(driver, 5).until(
								EC.presence_of_element_located((By.CSS_SELECTOR, ".sc-bdnxRM.denPjM table.Table-ziussd-1.EntryEventTable__StatsTable-sc-1d2xgo1-1.fHBHIK.jWFNPC"))
								)

							except:
								print("Table failed to appear")
							else:
								print("Table found")

								#create a new soup of DOM
								squad_page_soup = BeautifulSoup(driver.page_source, 'lxml')

								squad_data_tables = squad_page_soup.select(".sc-bdnxRM.denPjM table.Table-ziussd-1.EntryEventTable__StatsTable-sc-1d2xgo1-1.fHBHIK.jWFNPC")
								#print(squad_data_tables)

								for idx, table in enumerate(squad_data_tables):

									# squad status
									if idx == 0: 
										squad_status = "active"
									elif idx == 1:
										squad_status = "benched"

									table_rows = table.select("tbody tr")

									for row in table_rows:

										row_cells = row.select("td")


										# create temp dict to hold data
										temp_player_obj = {}

										temp_player_obj['squad_status'] = squad_status

										#row_cells[0] # information button

										#row_cells[1] # Captain / VC icon
										if len(row_cells[1].select("svg.TableCaptains__StyledCaptain-sc-1ub910p-0")) > 0:
											#print("* Captain *")
											temp_player_obj['captain_status'] = "Captain"

										elif len(row_cells[1].select("svg.TableCaptains__StyledViceCaptain-sc-1ub910p-1")) > 0:
											#print("* Vice Captain *")
											temp_player_obj['captain_status'] = "Vice Captain"

										else:
											temp_player_obj['captain_status'] = "None"

										#row_cells[2] # Name / Team / Position info
										player_information_container = row_cells[2].select("div.Media__Body-sc-94ghy9-2")

										temp_player_obj['player_name'] = player_information_container[0].select(".ElementInTable__Name-y9xi40-1")[0].get_text()
										temp_player_obj['player_team'] = player_information_container[0].select(".ElementInTable__Team-y9xi40-2")[0].get_text()
										temp_player_obj['player_position'] = player_information_container[0].select(".ElementInTable__Team-y9xi40-2")[0].parent.contents[1].get_text()

										#row_cells[3] # Points scored
										temp_player_obj['points_scored'] = row_cells[3].get_text()

										#row_cells[4] # Minutes played
										temp_player_obj['minutes_played'] = row_cells[4].get_text()
										
										#row_cells[5] # Goals scored
										temp_player_obj['goals_scored'] = row_cells[5].get_text()

										#row_cells[6] # Assists
										temp_player_obj['assists_made'] = row_cells[6].get_text()
										
										#row_cells[7] # Clean sheets
										temp_player_obj['clean_sheets'] = row_cells[7].get_text()
										
										#row_cells[8] # Goals conceded
										temp_player_obj['goals_conceded'] = row_cells[8].get_text()
										
										#row_cells[9] # Own goals
										temp_player_obj['own_goals_scored'] = row_cells[9].get_text()
										
										#row_cells[10] # Penalties saved
										temp_player_obj['penalty_saves'] = row_cells[10].get_text()
										
										#row_cells[11] # Penalties missed
										temp_player_obj['penalty_misses'] = row_cells[11].get_text()
										
										#row_cells[12] # Yellow cards
										temp_player_obj['yellow_cards'] = row_cells[12].get_text()
										
										#row_cells[13] # Red Cards
										temp_player_obj['red_cards'] = row_cells[13].get_text()
										
										#row_cells[14] # Saves
										temp_player_obj['saves_made'] = row_cells[14].get_text()
										
										#row_cells[15] # Bonus points
										temp_player_obj['bonus_points_scored'] = row_cells[15].get_text()
										
										#row_cells[16] # Bonus system score
										#row_cells[17] # Influence score (I)										
										#row_cells[18] # Creativity score (C)
										#row_cells[19] # Threat score (T)
										#row_cells[20] # ITC index


										data_dict[squad_gameweek]['squad'].append(temp_player_obj)	






				# print(data_dict)


				##### WRITE TO DATABASE #####
				for dict_entry in data_dict:

					filename = dirpath + '/GW' + dict_entry + '.json'

					print(f"Saving data to: {filename} ")

					#save temp json of player info
					with open(filename, 'w') as f:
						json.dump(data_dict[dict_entry], f, sort_keys=True, indent=4, separators=(',', ': '))


def accept_cookies():


	# Build the url
	url = "https://fantasy.premierleague.com/"

	try:
		print("Loading: ", url)

		#open the page
		driver.get(url)
		
		print("Waiting to accept cookies")
		#wait for the gameweek-by-gameweek data table container to appear
		WebDriverWait(driver, 30).until(
			EC.element_to_be_clickable((By.CSS_SELECTOR, "button._2hTJ5th4dIYlveipSEMYHH.BfdVlAo_cgSVjDUegen0F.js-accept-all-close"))
		)

	except:
		#if the table is not found, display an error message
		print("Error - button not found")
	
	else:
		# "Click" the list view toggle to reveal the data table
		driver.find_element_by_css_selector('button._2hTJ5th4dIYlveipSEMYHH.BfdVlAo_cgSVjDUegen0F.js-accept-all-close').click()
		print("Button clicked")


"""

- create a list of folders inside '/database'
- for each folder (i.e. each team):

	- determine if/what gameweeks exist (e.g. 'GW01.json', 'GW02.json', ...)
	- create a list of existing gameweeks files ([01, 02, 03, ...])

	- read 'player_info.json'
	- use 'manager_code' to open fpl 'gameweek history' page (e.g. https://fantasy.premierleague.com/entry/1035711/history)

	- scrape the data from that page in to a dict like so:

		"01": {
			"points scored": "val",
			"team value": "val",
			"key": "val"			
		}, 

		"02": {
			"points scored": "val",
			"team value": "val",
			"key": "val"			
		}...
		

	- for all gameweeks not yet in the database:
		- create a .json file in the database 
		- push the scraped data to a .json file


"""


#####
def execute():

	open_browser()

	accept_cookies()
	scrape()

	close_browser()


execute()
