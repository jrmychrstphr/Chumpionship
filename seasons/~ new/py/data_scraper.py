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

	root_filepath = "/Users/jrmychrstphr/Library/CloudStorage/Dropbox/Fantasy Football/Chumpionship/seasons/2023/data"

	for item in os.listdir(root_filepath):
		item_filepath = root_filepath + "/" + item
		
		#for each subfolder (ie, for each team)...
		if os.path.isdir(item_filepath):

			data_dict = {}
			list_of_subfolder_contents = os.listdir(item_filepath)

			if "player_info.json" in list_of_subfolder_contents:
				with open(item_filepath + "/player_info.json") as f:
						d = json.load(f)
						manager_code = d["manager_code"]
						manager_name = d["manager_name"]
			else: 
				print("Err - 'player_info.json' not found")

			existing_gameweeks = [x.replace("GW", "").replace(".json", "") for x in list_of_subfolder_contents if x.startswith("GW")]
			
			print(f"Scraping data for {manager_name}")
			table_css_selector = "table.Table-ziussd-1.dUELIG"

			# Build the url
			url = "https://fantasy.premierleague.com/entry/" + manager_code + "/history"

			try:
			#open the page
			print(f"Loading: {url}")
			driver.get(url)

				#wait for the fixture table to appear in DOM
				WebDriverWait(driver, 30).until(
					EC.presence_of_element_located((By.CSS_SELECTOR, table_css_selector))
				)


			except:
				#if the table is not found, display an error message
				print("Error - data table not detected")

			else:
				print("Success - table detected")

				#create soup of page DOM
				history_page_soup = BeautifulSoup(driver.page_source, 'lxml')

				##### SEASON HISTORY #####
				#locate table h3 text element 'This Season'
				season_data_table = history_page_soup.find("h3", text="This Season")

				# move up the soup DOM until the table is found
				while len(season_data_table.select(table_css_selector)) == 0:
					season_data_table = season_data_table.parent
					print("moving up the DOM looking for table...")
				else:
					season_data_table = season_data_table
					season_data_table_rows = season_data_table.select(table_css_selector + " tbody tr")
					print("Success - season data table located")
				
				if len(season_data_table_rows) > 0:
					print("Success - info found in season data table")

					for row in season_history_table_rows:

						# scrape data
						row_contents_array = row.contents
						season_data_gameweek = row_contents_array[0].find("a").get("href").split("/")[4]

						# gameweek (e.g. 01, 02, ...)
						season_data_gameweek = str("{0:0=2d}".format(int(gameweek)))

						if season_data_gameweek in existing_gameweeks:
							print(f"GW{season_data_gameweek} already exists")
						else: 
							print(f"Scraping season data for GW{season_data_gameweek}")

							"""
							0: gw
							1: overall rank
							2: 
							3: overall points
							4: gameweek rank
							5: gameweek points
							6: points on bench
							7: transfers made
							8: transfer cost
							9: squad value
							"""


							points_scored = float(row_contents_array[5].get_text())
							points_on_bench = float(row_contents_array[6].get_text())
							points_spent = float(row_contents_array[8].get_text())
							overall_total_points = float(row_contents_array[3].get_text())
							squad_value = float(row_contents_array[9].get_text())

							fixture_score = int(points_scored) - int(points_spent)

							# push data to data_dict
							data_dict[str(season_data_gameweek)] = {
							
								"points_scored": points_scored,
								"points_on_bench": points_on_bench,
								"points_spent": points_spent,
								"fixture_score": fixture_score,
								"squad_value": squad_value,
								"overall_total_points": overall_total_points,

								"chip_played": "None",

								"transfers_made": 0,
								"transfered_in": [],
								"transfered_out": [],

								"squad": [],

							}


				
				##### CHIPS #####
				#locate table h3 text element 'Chips'
				chips_data_table = history_page_soup.find("h3", text="Chips")

				# move up the soup DOM until the table is found
				while len(chips_data_table.select(table_css_selector)) == 0:
					chips_data_table = chips_data_table.parent
					print("moving up the DOM looking for table...")
				else:
					chips_data_table = chips_data_table
					chips_data_table_rows = chips_data_table.select(table_css_selector + " tbody tr")
					print("Success - chips data table located")
				
				if len(chips_data_table_rows) > 0:
					print("Success - info found in chips data table")

					for row in chips_data_table_rows:
						row_contents_array = row.contents

						# check this after a chip is played
						chip_gameweek = row_contents_array[2].find("a").get("href").split("/")[4]
						chip_gameweek = str("{0:0=2d}".format(int(chip_gameweek)))

						if chip_gameweek in existing_gameweeks:
							print(f"GW{chip_gameweek} already exists")
						else:
							print(f"Scraping chips data for GW{chip_gameweek}")
							# push data to data_dict
							chip_name = row_contents_array[1].get_text().title()
							data_dict[chip_gameweek]['chip_played'] = chip_name
							print(f"{chip_name} played in GW{chip_gameweek}")



				##### TRANSFERS #####

				# Build the url
				transfers_url = "https://fantasy.premierleague.com/entry/"+manager_code+"/transfers"

				try:
					print(f"Loading transfers page for {manager_name}")

					#open the page
					driver.get(transfers_url)

					#wait for the gameweek-by-gameweek data table container to appear
					WebDriverWait(driver, 5).until(
					EC.presence_of_element_located((By.CSS_SELECTOR, table_css_selector))
					)


				except:
					#if the table is *not* found...
					try:
						#Look for the page placeholder instead
						WebDriverWait(driver, 5).until(
						EC.text_to_be_present_in_element((By.CSS_SELECTOR, ".Layout__Main-eg6k6r-1"), "No transfers have been made")
						)

					except:
						print("Err – Transfers")
					else:
						print(f"{manager_name} is yet to make a transfer")
						transfers_obj = False

				else:
					#if the table is found...
					print("Success - transfers data table detected")

					transfers_page_soup = BeautifulSoup(driver.page_source, 'lxml')

					#locate 'This Season' title
					transfers_history_table = transfers_page_soup.find("h2", text="Transfers")

					# move up the soup DOM until the table is found
					while len(transfers_history_table.select(table_css_selector)) == 0:
						transfers_history_table = transfers_history_table.parent
						print("moving up the DOM looking for table...")
					else:
						transfers_history_table = transfers_history_table
						transfers_history_table_rows = transfers_history_table.select(table_css_selector + " tbody tr")
						print("Success - transfers data table located")
					
					if len(transfers_history_table_rows) > 0:
						print("Success - info found in transfers data table")

						for row in transfers_history_table_rows:

							row_contents_array = row.contents

							# define gameweek
							transfers_gameweek = str("{0:0=2d}".format(int(row_contents_array[3].get_text().lower().replace('gw', ''))))

							if transfers_gameweek in existing_gameweeks:
								print(f"GW{transfers_gameweek} already exists")
							else:
								print(f"Scraping transfer data for GW{transfers_gameweek}")

								# add 1 to the total transfers made in that gamweek
								data_dict[transfers_gameweek]["transfers_made"] += 1

								transfered_in = row_contents_array[1].get_text()
								transfered_out = row_contents_array[2].get_text()

								data_dict[transfers_gameweek]["transfered_in"].append(transfered_in)
								data_dict[transfers_gameweek]["transfered_out"].append(transfered_out)

				
				##### SQUAD ##### -- this bit may need updating
				gameweek_anchors = season_history_data_table.find_all("a")

				for anchor in gameweek_anchors:

					href = anchor.get("href")
					squad_gameweek = str("{0:0=2d}".format(int(href.split("/")[4])))

					if squad_gameweek not in existing_gameweeks:

						try:
							print(f"Loading squad page for GW{squad_gameweek}")

							driver.get("https://fantasy.premierleague.com" + href)

							#wait for the data table container to appear
							WebDriverWait(driver, 5).until(
							EC.presence_of_element_located((By.CSS_SELECTOR, ".Layout__Main-eg6k6r-1 a.Tab__TabLink-sc-19t48gi-1.jIjLCn"))
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
								EC.presence_of_element_located((By.CSS_SELECTOR, ".Layout__Main-eg6k6r-1 table.Table-ziussd-1.EntryEventTable__StatsTable-sc-1d2xgo1-1.dUELIG.gTOduH"))
								)

							except:
								print("Table failed to appear")
							else:
								print("Table found")

								#create a new soup of DOM
								squad_page_soup = BeautifulSoup(driver.page_source, 'lxml')

								squad_data_tables = squad_page_soup.select(".Layout__Main-eg6k6r-1 table.Table-ziussd-1.EntryEventTable__StatsTable-sc-1d2xgo1-1.dUELIG.gTOduH")
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
										temp_player_obj['player_team'] = player_information_container[0].select(".ElementInTable__Team-y9xi40-3")[0].get_text()
										temp_player_obj['player_position'] = player_information_container[0].select(".ElementInTable__Team-y9xi40-3")[0].parent.contents[1].get_text()

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



			##### WRITE TO DATABASE #####
			for dict_entry in data_dict:

				filename = item_filepath + "/GW" + dict_entry + '.json'
				print(f"Saving data to: {filename} ")

				#save temp json of player info
				with open(filename, "w") as f:
					json.dump(data_dict[dict_entry], f, sort_keys=True, indent=4, separators=(",", ": "))



#####
def execute():

	open_browser()

	import cookies
	cookies.accept_cookies(driver)

	scrape()
	close_browser()


execute()
