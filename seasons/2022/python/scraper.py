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


############
def return_manager_codes_as_list():

	manager_codes = database['league_data']["entrant_id_list"].copy()
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
# scrapes performance data for  #
def return_lookup_opponent_code(manager_code, gameweek):

	for key, val in database['player_data'].items():

		if val['manager_info']['fpl_code'] == manager_code:
			opponent_code = val['fixtures'][gameweek]['opponent_manager_fpl_code']
			return opponent_code


###############
# scrapes:
# --- performance data from the history page
# for each manager in the league

def scrape_gw_performance_data():

	for manager_code in return_manager_codes_as_list():

		if 'gw_performance' not in database['player_data'][manager_code]:
			database['player_data'][manager_code]['gw_performance'] = {}

		# Build the url
		url = "https://fantasy.premierleague.com/entry/"+manager_code+"/history"

		try:
			print("Loading season history page for ", return_lookup_manager_fullname(manager_code))

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
			print("Success! Lets scrape some data")

			#create soup of DOM
			history_page_soup = BeautifulSoup(driver.page_source, 'lxml')

			#locate 'This Season' table
			season_history = history_page_soup.find("h3", text="This Season")

			#move up the soup DOM until the table is found
			while len(season_history.select('.Table-ziussd-1.fHBHIK')) == 0:
				season_history = season_history.parent
			else:
				season_history = season_history

			season_history_table_rows = season_history.select('.Table-ziussd-1.fHBHIK tbody tr')

			for row in season_history_table_rows:

				row_contents_array = row.contents
				row_gameweek = row_contents_array[0].find('a').get('href').split('/')[4]

				gw = str("{0:0=2d}".format(int(row_gameweek)))

				points_scored = int(float(row_contents_array[1].get_text()))
				points_on_bench = int(float(row_contents_array[2].get_text()))
				points_spent = int(float(row_contents_array[5].get_text()))
				overall_total_points = int(float(row_contents_array[6].get_text()))
				squad_value = int(float(row_contents_array[8].get_text()))

				global_overall_rank = int(float(row_contents_array[3].get_text().replace(",","")))
				global_gameweek_rank= int(float(row_contents_array[7].get_text().replace(",","")))

				fixture_score = int(points_scored) - int(points_spent)

				if 'gw_performance' not in database['player_data'][manager_code]:
					database['player_data'][manager_code]['gw_performance'] = {}

				if gw not in database['player_data'][manager_code]['gw_performance']:
					database['player_data'][manager_code]['gw_performance'][gw] = {}

				database['player_data'][manager_code]['gw_performance'][gw]['points_scored'] = points_scored
				database['player_data'][manager_code]['gw_performance'][gw]['points_on_bench'] = points_on_bench
				database['player_data'][manager_code]['gw_performance'][gw]['points_spent'] = points_spent
				database['player_data'][manager_code]['gw_performance'][gw]['fixture_score'] = fixture_score
				database['player_data'][manager_code]['gw_performance'][gw]['squad_value'] = squad_value
				database['player_data'][manager_code]['gw_performance'][gw]['overall_total_points'] = overall_total_points

				database['player_data'][manager_code]['gw_performance'][gw]['global_overall_rank'] = global_overall_rank
				database['player_data'][manager_code]['gw_performance'][gw]['global_gameweek_rank'] = global_gameweek_rank
				


				for fixture in database['fixture_list'][gw]:
					if fixture['away_team'] == manager_code:
						opp_code = fixture['home_team']
					elif fixture['home_team'] == manager_code:
						opp_code = fixture['away_team']

				if opp_code:
					print("Fixture opponent found")
					database['player_data'][manager_code]['gw_performance'][gw]['fixture_opponent_manager_code'] = opp_code
				else:
					print("Error! Fixture opponentnot found")



				#locate Chips played table
				chips_history = history_page_soup.find("h3", text="Chips")

				#move up the soup DOM until the table is found
				while len(chips_history.select('.Table-ziussd-1.fHBHIK')) == 0:
					chips_history = chips_history.parent
				else:
					table_rows = chips_history.select('.Table-ziussd-1.fHBHIK tbody tr')

				chips_played = {}

				if len(table_rows) > 0:
					for row in table_rows:

						row_contents_array = row.contents

						chip_name = row_contents_array[1].get_text()
						chip_gameweek = row_contents_array[2].find('a').get('href').split('/')[4]

						chip_gw = str("{0:0=2d}".format(int(chip_gameweek)))

						chips_played[chip_gw] = chip_name


				#cycle through scraped data and add the chips
				for key, val in database['player_data'][manager_code]['gw_performance'].items():

					if key in chips_played:
						#print('Chip played in gw', key, ': ', chips_played[key])
						chip = chips_played[key]
					else:
						chip = 'None'

					database['player_data'][manager_code]['gw_performance'][key]['chip_played'] = chip


			# ADD PLAYER SCRAPE SCRIPT HERE #
			gameweek_anchors = season_history.find_all('a')

			for anchor in gameweek_anchors:

				href = anchor.get('href')
				gameweek = str("{0:0=2d}".format(int(href.split('/')[4])))

				try:
					print("Loading GW", gameweek, "for", return_lookup_manager_fullname(manager_code))

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


						if 'squad' not in database['player_data'][manager_code]['gw_performance'][gameweek]:
							database['player_data'][manager_code]['gw_performance'][gameweek]['squad'] = []

						#create a new soup of DOM
						gameweek_page_soup = BeautifulSoup(driver.page_source, 'lxml')

						player_data_tables = gameweek_page_soup.select(".sc-bdnxRM.denPjM table.Table-ziussd-1.EntryEventTable__StatsTable-sc-1d2xgo1-1.fHBHIK.jWFNPC")
						#print(player_data_tables)

						for idx, table in enumerate(player_data_tables):

							if idx == 0: 
								squad_status = "active"
							elif idx == 1:
								squad_status = "benched"

							table_rows = table.select("tbody tr")
							for row in table_rows:
								row_cells = row.select("td")
								temp_player_obj = {}

								temp_player_obj['squad_status'] = squad_status

								#row_cells[0] # information button

								#row_cells[1] # Captain / VC icon
								if len(row_cells[1].select("svg.TableCaptains__StyledCaptain-sc-1ub910p-0")) > 0:
									#print("* Captain *")
									temp_player_obj['captain_status'] = "captain"
								elif len(row_cells[1].select("svg.TableCaptains__StyledViceCaptain-sc-1ub910p-1")) > 0:
									#print("* Vice Captain *")
									temp_player_obj['captain_status'] = "vice_captain"
								else:
									temp_player_obj['captain_status'] = "none"

								#row_cells[2] # Name / Team / Position info
								player_information_container = row_cells[2].select("div.Media__Body-sc-94ghy9-2")

								temp_player_obj['player_name'] = player_information_container[0].select(".ElementInTable__Name-y9xi40-1")[0].get_text()
								temp_player_obj['player_team'] = player_information_container[0].select(".ElementInTable__Team-y9xi40-2")[0].get_text()
								temp_player_obj['player_position'] = player_information_container[0].select(".ElementInTable__Team-y9xi40-2")[0].parent.contents[1].get_text()

								#row_cells[3] # Points scored
								temp_player_obj['points_scored'] = row_cells[3].get_text()

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

								database['player_data'][manager_code]['gw_performance'][gameweek]['squad'].append(temp_player_obj)

		

		# ADD TRANSFER SCRAPE SCRIPT IN HERE #

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
					EC.text_to_be_present_in_element((By.CSS_SELECTOR, ".Layout__Main-eg6k6r-1.wXYnc"), "No transfers have been made yet for this team.")
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
					

		for gameweek in database['player_data'][manager_code]['gw_performance']:
			if (transfers_obj == False) or (gameweek not in transfers_obj):
				t = int(0)
			else:
				t = int(transfers_obj[gameweek])

			database['player_data'][manager_code]['gw_performance'][gameweek]['transfers_made'] = t



	#x-ref Data to define fixture results
	for manager_code in return_manager_codes_as_list():
		# for each gw in the perf data dict
		for gw, val in database['player_data'][manager_code]['gw_performance'].items():

			fixture_score = val['fixture_score']
			opponent_code = val['fixture_opponent_manager_code']			
			opponent_fixture_score = database['player_data'][opponent_code]['gw_performance'][gw]['fixture_score']

			if fixture_score > opponent_fixture_score:
				result = 'w'
			elif fixture_score < opponent_fixture_score:
				result = 'l'
			elif fixture_score == opponent_fixture_score:
				result = 'd'
			else:
				result - 'Error'
				print('Error: Unable to determine result')
				print('Manager:', return_lookup_manager_fullname(manager_code))
				print('GW: ', gw)


			database['player_data'][manager_code]['gw_performance'][gw]['fixture_result'] = result



###############
# write data to json file
def write_to_json_file(filename, input_data):
    with open(filename + '.json', 'w') as json_file:
        json.dump(input_data, json_file, sort_keys=True, indent=4, separators=(',', ': '))


###############
# compiles season_perfomance  #
# using data from gw_performance (input_data) #
# for each manager in the dataset #
def compile_season_performance():

	gw_count_array = []

	# for each player
	for manager_code in return_manager_codes_as_list():

		if 'season_performance' not in database['player_data'][manager_code]:
			database['player_data'][manager_code]['season_performance'] = {}

		gw_performance_data = database['player_data'][manager_code]['gw_performance']

		season_performance = {}

		#declare lists / arrays to store data
		points_scored_array = []
		points_spent_array = []
		fixture_score_array = []

		points_on_bench_array = []
		squad_value_array = []

		global_overall_rank_array = []
		global_gameweek_rank_array = []
		fixture_result_array = []

		#transfers_made_array = []

		opponent_score_array = []
		fixture_score_running_total_array = []
		

		# for each gameweek
		for gw, val in gw_performance_data.items():

			# push data to arrays

			#transfers_made_array.append(val['transfers_made'])
			
			points_scored_array.append(val['points_scored'])
			points_spent_array.append(val['points_spent'])
			points_on_bench_array.append(val['points_on_bench'])
			fixture_score_array.append(val['fixture_score'])
			squad_value_array.append(val['squad_value'])

			global_overall_rank_array.append(val['global_overall_rank'])
			global_gameweek_rank_array.append(val['global_gameweek_rank'])


			fixture_score_running_total_array.append(sum(fixture_score_array))
			
			fixture_result_array.append(val['fixture_result'])

			opponent_code = val['fixture_opponent_manager_code']
			opponent_score = database['player_data'][opponent_code]['gw_performance'][gw]['fixture_score']
			opponent_score_array.append(opponent_score)

			if gw not in gw_count_array:
				gw_count_array.append(gw)


		# use arrays to calculate totals

		"""
		transfers_made_total = sum(transfers_made_array)
		season_performance['transfers_made_array'] = transfers_made_array
		season_performance['transfers_made_total'] = transfers_made_total
		"""

		points_scored_total = sum(points_scored_array)
		season_performance['points_scored_array'] = points_scored_array
		season_performance['points_scored_total'] = points_scored_total

		points_spent_total = sum(points_spent_array)
		season_performance['points_spent_array'] = points_spent_array
		season_performance['points_spent_total'] = points_spent_total

		fixture_score_total = sum(fixture_score_array)
		season_performance['fixture_score_array'] = fixture_score_array
		season_performance['fixture_score_total'] = fixture_score_total
		season_performance['fixture_score_running_total_array'] = fixture_score_running_total_array

		points_on_bench_total = sum(points_on_bench_array)
		season_performance['points_on_bench_array'] = points_on_bench_array
		season_performance['points_on_bench_total'] = points_on_bench_total

		season_performance['squad_value_array'] = squad_value_array

		opponent_score_total = sum(opponent_score_array)
		season_performance['opponent_score_array'] = opponent_score_array
		season_performance['opponent_score_total'] = opponent_score_total

		season_performance['global_overall_rank_array'] = global_overall_rank_array

		season_performance['global_gameweek_rank_array'] = global_gameweek_rank_array

		season_performance['fixture_result_array'] = fixture_result_array

		league_points_array = []
		league_points_running_total_array = []
		
		for x in fixture_result_array:
			if x.lower() == 'w':
				p = 3
			elif x.lower() == 'l':
				p = 0
			elif x.lower() == 'd':
				p = 1
			else:
				print('Error!')

			league_points_array.append(p)
			league_points_running_total_array.append(sum(league_points_array))


		season_performance['league_points_array'] = league_points_array
		season_performance['league_points_total'] = sum(league_points_array)
		season_performance['league_points_running_total_array'] = league_points_running_total_array


		database['player_data'][manager_code]['season_performance'] = season_performance


	## calculate round-by-round league position
	
	# declare a dict to store round-by-round pos data for each manager
	temp_league_pos_data = {}

	# for each gameweek in the data:
	for i, gw in enumerate(gw_count_array):

		# declare an empty array
		g = []

		# for each manager in the league:
		for manager_code in return_manager_codes_as_list():

			# push a dict with:
			m = {}
			
			# manager code
			m['manager_code'] = manager_code
			# total league points
			m['league_points'] = database['player_data'][manager_code]['season_performance']['league_points_running_total_array'][i]
			# total score
			m['total_score'] = database['player_data'][manager_code]['season_performance']['fixture_score_running_total_array'][i]

			g.append(m)


		# order the array by (1) league points, (2) overall score
		g = sorted(g, key = lambda x: (x['league_points'], x['total_score']), reverse=True)

		# use the ordered array to determine league position that gameweek
		for idx, x in enumerate(g):

			manager_code = g[idx]['manager_code']

			if idx > 0:

				# if league points and total score  == the previous entry in the array,
				if g[idx]['league_points'] == g[idx-1]['league_points'] and g[idx]['total_score'] == g[idx-1]['total_score']:
					# the position is the same as the previous entry
					pos = pos

				#else, the position is determined by the item's position in the sorted list
				else:
					pos = idx+1

			#the league pos for the first item in the sorted list will always be 1
			else:
				pos = idx+1

			# if the temp_dict doesn't contain a key matching the manager_code
			if manager_code not in temp_league_pos_data:
				# add that key, and blank array to store league pos data
				temp_league_pos_data[manager_code] = []

			# push the league pos to that manager's array
			temp_league_pos_data[manager_code].append(pos)

	# cycle through temp obj and push to database
	for key, val in temp_league_pos_data.items():

		manager_code = key

		database['player_data'][manager_code]['season_performance']['league_position_array'] = val



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

	#load the clean database file
	global database
	database = return_load_json_file('../database/_versions/chumpionship_2022_database---new')

	open_browser()

	scrape_gw_performance_data()
	compile_season_performance()

	"""
	gw_performance_data = return_scrape_and_compile_gw_performance_data()
	gw_performance_data = covid_fix(gw_performance_data)
	push_to_database_gw_performance_data(gw_performance_data)


	season_performance_data = return_compile_season_performance(gw_performance_data)
	push_to_database_season_performance_data(season_performance_data)
	"""


	datestamp = return_create_date_stamp()
	#save a version in the version folder
	write_to_json_file('../database/_versions/chumpionship_2022_database---' + datestamp, database)
	#overwrite the core database file
	write_to_json_file('../database/chumpionship_2022_database', database)

	close_browser()

execute()