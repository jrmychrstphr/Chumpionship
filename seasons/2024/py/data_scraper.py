# ============================================================
# This script scrapes data from the FPL site for all teams in 
# the league, and exports a .json file for each GW played
# It also scans 'data' to assess which GWs are already in the 
# directory, eliminating double-ups and speeding-up the process
# ============================================================

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

	data_dir_path = "../data"

	for item in os.listdir(data_dir_path):
		item_filepath = data_dir_path + "/" + item
		
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
			print(f"Existing gameweeks: {existing_gameweeks}")

			# ===== Edit this if needed =====
			table_css_selector = "div.Layout__Main-eg6k6r-1 table.Table-ziussd-1.dUELIG"

			
			# ===== HISTORY PAGE: GW data and Chips =====
			# Build the url
			history_page_url = "https://fantasy.premierleague.com/entry/" + manager_code + "/history"

			try:
				#open the page
				print(f"Loading: {history_page_url}")
				driver.get(history_page_url)

				#wait for the fixture table to appear in DOM
				WebDriverWait(driver, 30).until(
					EC.presence_of_element_located((By.CSS_SELECTOR, table_css_selector))
				)


			except:
				#if the table is not found, display an error message
				print("Error - data table not detected")
				exit()

			else:
				print("Success - table detected")
				pass

			#create soup of page DOM
			history_page_soup = BeautifulSoup(driver.page_source, 'lxml')

			##### GW data #####
			#locate table h3 text element 'This Season'
			season_data_table = history_page_soup.find("h3", text="This Season")
			print(f"Found h3 'This Season'")

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

				for row in season_data_table_rows:

					# scrape data
					row_contents_array = row.contents
					season_data_gameweek = row_contents_array[0].find("a").get("href").split("/")[4]

					# gameweek (e.g. 01, 02, ...)
					season_data_gameweek = str("{0:0=2d}".format(int(season_data_gameweek)))

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

						fixture_score = float(points_scored - points_spent)

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
							"vice_captain": "",
							"captain": "",

						}
			else:
				print("No info found in season data table")


			
			##### CHIPS #####
			#locate table h3 text element 'Chips'
			chips_data_table = history_page_soup.find("h3", text="Chips")
			print(f"Found h3 'Chips'")

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
						data_dict[chip_gameweek].update({"chip_played": str(chip_name)})
						print(f"{chip_name} played in GW{chip_gameweek}")
			else:
				print("No info found in chips data table")



			##### TRANSFERS #####

			# Build the url
			transfers_url = "https://fantasy.premierleague.com/entry/"+manager_code+"/transfers"

			#open the page
			driver.get(transfers_url)
			print(f"Loading transfers page for {manager_name}")

			try:
				#wait for the gameweek-by-gameweek data table container to appear
				WebDriverWait(driver, 10).until(
				EC.presence_of_element_located((By.CSS_SELECTOR, table_css_selector))
				)
			except:
				#if the table is *not* found...
				print(f"Err- Data table not detected")

				try:
					#Look for the page placeholder instead
					print(f"Searching for transfers message...")
					WebDriverWait(driver, 5).until(
					EC.text_to_be_present_in_element((By.CSS_SELECTOR, ".Layout__Main-eg6k6r-1"), "No transfers have been made")
					)

				except:
					print(f"Err - unable to detect transfers")
					transfers_status = False
				else:
					print(f"{manager_name} is yet to make a transfer")
					transfers_status = False

			else:
				#if the table is found...
				print("Success - transfers data table detected")
				transfers_status = True


			if transfers_status:
				transfers_page_soup = BeautifulSoup(driver.page_source, 'lxml')

				#locate 'This Season' title
				transfers_history_table = transfers_page_soup.find("h2", text="Transfers")
				print(f"Found h2 'Transfers'")

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
							print(f"Transfers: GW{transfers_gameweek} data already exists")
						else:
							print(f"Scraping transfer data for GW{transfers_gameweek}")

							# add 1 to the total transfers made in that gamweek
							data_dict[transfers_gameweek]["transfers_made"] += 1

							transfered_in = row_contents_array[1].get_text()
							transfered_out = row_contents_array[2].get_text()

							data_dict[transfers_gameweek]["transfered_in"].append(transfered_in)
							data_dict[transfers_gameweek]["transfered_out"].append(transfered_out)

			
			##### SQUAD ##### -- this bit may need updating
			gameweek_anchors = season_data_table.find_all("a")

			for anchor in gameweek_anchors:

				href = anchor.get("href")
				squad_gameweek = str("{0:0=2d}".format(int(href.split("/")[4])))

				if squad_gameweek in existing_gameweeks:
					print(f"Squad: GW{squad_gameweek} data already exists")
				else:
					print(f"Loading squad page for GW{squad_gameweek}")
					driver.get("https://fantasy.premierleague.com" + href)

					try:
						#wait for the 'List View' button' to be clickable
						WebDriverWait(driver, 30).until(
						EC.element_to_be_clickable((By.CSS_SELECTOR, "div.Layout__Main-eg6k6r-1 a.Tab__TabLink-sc-19t48gi-1.jIjLCn"))
						)
					except:
						print("Err - page failed to load")
						exit()
					else:
						print("Success - page loaded")
						pass

					# "Click" the list view toggle button to reveal the data table
					driver.find_element(By.LINK_TEXT, "List View").click()
					print("'List View' button clicked")

					data_table_css_selector = "div.Layout__Main-eg6k6r-1 table.Table-ziussd-1.EntryEventTable__StatsTable-sc-1d2xgo1-1.dUELIG.gTOduH"

					try:
						print("Waiting for data tables to appear...")

						#wait for the gameweek-by-gameweek data table container to appear
						WebDriverWait(driver, 30).until(						
						EC.presence_of_element_located((By.CSS_SELECTOR, data_table_css_selector))
						)

					except:
						print("Table failed to appear")
					else:
						print("Table found")

						#create a new soup of DOM
						squad_page_soup = BeautifulSoup(driver.page_source, 'lxml')

						squad_data_tables = squad_page_soup.select(data_table_css_selector)
						#print(squad_data_tables)

						for idx, table in enumerate(squad_data_tables):

							# squad status
							if idx == 0: 
								squad_status = "active"
							elif idx == 1:
								squad_status = "benched"

							table_rows = table.select("tbody tr")

							temp_squad = []

							for row in table_rows:

								row_cells = row.select("td")

								player_information_container = row_cells[2].select("div.Media__Body-sc-94ghy9-2")
								player_name = player_information_container[0].select(".ElementInTable__Name-y9xi40-1")[0].get_text()
								player_team = player_information_container[0].select(".ElementInTable__Team-y9xi40-3")[0].get_text()
								player_position = player_information_container[0].select(".ElementInTable__Team-y9xi40-3")[0].parent.contents[1].get_text()

								if len(row_cells[1].select("svg.TableCaptains__StyledCaptain-sc-1ub910p-0")) > 0:
									captain_status = "captain"
									data_dict[squad_gameweek].update({"captain": str(player_name) + " (" + str(player_team) + ", " + str(player_position) + ")"})
								elif len(row_cells[1].select("svg.TableCaptains__StyledViceCaptain-sc-1ub910p-1")) > 0:
									captain_status = "vice captain"
									data_dict[squad_gameweek].update({"vice_captain": str(player_name) + " (" + str(player_team) + ", " + str(player_position) + ")"})
								else:
									captain_status = "None"


								temp_player_obj = {

									"captain_status": str(captain_status),
									"squad_status": str(squad_status),

									"player_name": str(player_name),
									"player_team": str(player_team),
									"player_position": str(player_position),

									"points_scored": str(row_cells[3].get_text()),
									"minutes_played": str(row_cells[4].get_text()),
									"goals_scored": str(row_cells[5].get_text()),
									"assists_made": str(row_cells[6].get_text()),
									"clean_sheets": str(row_cells[7].get_text()),
									"goals_conceded": str(row_cells[8].get_text()),
									"own_goals": str(row_cells[9].get_text()),
									"penalty_saves": str(row_cells[10].get_text()),
									"penalty_misses": str(row_cells[11].get_text()),
									"yellow_cards": str(row_cells[12].get_text()),
									"red_cards": str(row_cells[13].get_text()),
									"saves_made": str(row_cells[14].get_text()),
									"bonus_points_scored": str(row_cells[15].get_text()),
									"bonus_points_rating": str(row_cells[16].get_text()),
								
									"influence": str(row_cells[17].get_text()),
									"creativity": str(row_cells[18].get_text()),
									"threat": str(row_cells[19].get_text()),
									"ict_index": str(row_cells[20].get_text()),
									"game_started": str(row_cells[21].get_text()),
									"expected_goals_scored": str(row_cells[22].get_text()),
									"expected_assists": str(row_cells[23].get_text()),
									"expected_goal_involvement": str(row_cells[24].get_text()),
									"expeceted_goals_conceded": str(row_cells[25].get_text()),
								}

								data_dict[squad_gameweek]["squad"].append(temp_player_obj)




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
