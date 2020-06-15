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
def return_scrape_and_compile_gw_performance_data():

	manager_code_list = return_manager_codes_as_list()

	exclude_list = []

	# if database already contains gw data
	if 'gw_performance' in database['player_data'][manager_code_list[0]]:

		# ask user if existing data should be replaced
		print('Database contains existing gw_performance data')
		user_input = input('Update existing data? (Y/N): ')

		if str(user_input.upper()) == "N":
			for key, val in database['player_data'][manager_code_list[0]]['gw_performance'].items():
				exclude_list.append(key)

		print(exclude_list)

	else:
		print('database does not contain existing gw_performance data')


	#declare dict to store data in 
	performance_data = {}


	for manager_code in manager_code_list:

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

				gw = str("{0:0=2d}".format(int(row_gameweek)))

				# if gw is on the exclusion_list, push data from database to performance data temp dict
				if gw in exclude_list:

					print(row_gameweek + ' in exclusion list')
					scraped_data[gw] = database['player_data'][manager_code]['gw_performance']
					print('Data copied from database')

				# else, scrape that data from the page and push to dict
				else: 

					points_scored = float(row_contents_array[1].get_text())
					points_on_bench = float(row_contents_array[2].get_text())
					#transfers_made = float(row_contents_array[4].get_text())
					points_spent = float(row_contents_array[5].get_text())
					overall_total_points = float(row_contents_array[6].get_text())
					squad_value = float(row_contents_array[8].get_text())

					fixture_score = points_scored - points_spent


					if gw not in scraped_data:
						scraped_data[gw] = {}

					scraped_data[gw]['points_scored'] = points_scored
					scraped_data[gw]['points_on_bench'] = points_on_bench
					scraped_data[gw]['points_spent'] = points_spent
					scraped_data[gw]['fixture_score'] = fixture_score
					#scraped_data[gw]['transfers_made'] = transfers_made
					scraped_data[gw]['squad_value'] = squad_value
					scraped_data[gw]['overall_total_points'] = overall_total_points

					fixture_opponent_manager_code = return_lookup_opponent_code(manager_code, gw)
					fixture_opponent_team_name = return_lookup_team_name(fixture_opponent_manager_code)
					fixture_opponent_manager_fullname = return_lookup_manager_fullname(fixture_opponent_manager_code)
					
					scraped_data[gw]['fixture_opponent_manager_code'] = fixture_opponent_manager_code
					scraped_data[gw]['fixture_opponent_team_name'] = fixture_opponent_team_name
					scraped_data[gw]['fixture_opponent_manager_fullname'] = fixture_opponent_manager_fullname


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


					#cycle through scraped data and add the chips
					for key, val in scraped_data.items():

						if key in chips_played:
							#print('Chip played in gw', key, ': ', chips_played[key])
							chip = chips_played[key]
						else:
							chip = 'None'

						scraped_data[key]['chip_played'] = chip


		performance_data[manager_code] = scraped_data


	## scrape tranfer data
	# declare dict to store data in 
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

				#print (row)

				row_contents_array = row.contents
				row_gameweek_string = row_contents_array[3].get_text()
				gw = str("{0:0=2d}".format(int(row_gameweek_string.lower().replace('gw', ''))))

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

		for key, val in performance_data[manager_code].items():

			# if gw is on the exclusion_list, push data from database to performance data temp dict
			if key not in exclude_list:

				if key not in transfer_data[manager_code]:
					transfers_made = 0
				else:
					transfers_made = transfer_data[manager_code][key]

				#print( 'Transfers in gw' + str(key) + ': ' + str(transfers_made))
				performance_data[manager_code][key]['transfers_made'] = transfers_made

			else:

				print(key + ' in exclusion list')
				performance_data[manager_code][key]['transfers_made'] = database['player_data'][manager_code]['gw_performance'][key]['transfers_made']
				print('Data copied from database')

	#print(performance_data)


	#x-ref perf data dict to define fixture results
	for manager_code in manager_code_list:

		# for each gw in the perf data dict

		for key, val in performance_data[manager_code].items():

			if key not in exclude_list:

				fixture_score = val['fixture_score']
				opponent_code = val['fixture_opponent_manager_code']

				opponent_fixture_score = performance_data[opponent_code][key]['fixture_score']

				if fixture_score > opponent_fixture_score:
					result = 'W'
				elif fixture_score < opponent_fixture_score:
					result = 'L'
				elif fixture_score == opponent_fixture_score:
					result = 'D'
				else:
					result - 'Error'
					print('Error: Unable to determine result')
					print('Manager:', return_lookup_manager_fullname(manager_code))
					print('GW: ', key)


				performance_data[manager_code][key]['fixture_result'] = result


	return performance_data


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


###############
# compiles season_perfomance  #
# using data from gw_performance (input_data) #
# for each manager in the dataset #
def return_compile_season_performance(input_data):

	#print(input_data)

	# declare a dict to store the output data
	output_data = {}


	# for each player
	for key, val in input_data.items():

		manager_code = key
		gw_performance_data = val


		season_performance = {}

		#declare lists / arrays to store data
		transfers_made_array = []
		fixture_score_array = []
		points_scored_array = []
		points_spent_array = []
		points_on_bench_array = []
		opponent_score_array = []

		fixture_score_running_total_array = []
		
		result_array = []

		# for each gameweek
		for key, val in gw_performance_data.items():

			gw = key

			# push data to arrays

			transfers_made_array.append(val['transfers_made'])
			points_scored_array.append(val['points_scored'])
			points_spent_array.append(val['points_spent'])
			points_on_bench_array.append(val['points_on_bench'])
			fixture_score_array.append(val['fixture_score'])

			fixture_score_running_total_array.append(sum(fixture_score_array))
			
			result_array.append(val['fixture_result'])

			opponent_code = val['fixture_opponent_manager_code']
			opponent_score = input_data[opponent_code][gw]['fixture_score']

			opponent_score_array.append(opponent_score)


		# use arrays to calculate totals

		transfers_made_total = sum(transfers_made_array)
		season_performance['transfers_made_array'] = transfers_made_array
		season_performance['transfers_made_total'] = transfers_made_total

		fixture_score_total = sum(fixture_score_array)
		season_performance['fixture_score_array'] = fixture_score_array
		season_performance['fixture_score_total'] = fixture_score_total

		season_performance['fixture_score_running_total_array'] = fixture_score_running_total_array

		points_scored_total = sum(points_scored_array)
		season_performance['points_scored_array'] = points_scored_array
		season_performance['points_scored_total'] = points_scored_total

		points_spent_total = sum(points_spent_array)
		season_performance['points_spent_array'] = points_spent_array
		season_performance['points_spent_total'] = points_spent_total

		points_on_bench_total = sum(points_on_bench_array)
		season_performance['points_on_bench_array'] = points_on_bench_array
		season_performance['points_on_bench_total'] = points_on_bench_total

		opponent_score_total = sum(opponent_score_array)
		season_performance['opponent_score_array'] = opponent_score_array
		season_performance['opponent_score_total'] = opponent_score_total


		result_count = {}
		result_count['W'] = result_array.count('W')
		result_count['D'] = result_array.count('D')
		result_count['L'] = result_array.count('L')

		season_performance['result_array'] = result_array
		season_performance['result_count'] = result_count


		league_points_array = []
		league_points_running_total_array = []
		
		for x in result_array:
			if x == 'W':
				p = 3
			elif x == 'L':
				p = 0
			elif x == 'D':
				p = 1
			else:
				print('Error!')

			league_points_array.append(p)
			league_points_running_total_array.append(sum(league_points_array))


		league_points_total = sum(league_points_array)
		season_performance['league_points_array'] = league_points_array
		season_performance['league_points_total'] = league_points_total
		season_performance['league_points_running_total_array'] = league_points_running_total_array


		output_data[manager_code] = season_performance


	## calculate round-by-round league position
	
	# determine how many gameweeks the dataset contains
	manager_codes_list = return_manager_codes_as_list()
	gameweek_array = []

	# declare a dict to store round-by-round pos data for each manager
	temp_league_pos_data = {}

	for key, val in input_data[manager_codes_list[0]].items():
		gameweek_array.append(key)


	# for each gameweek in the data:
	for i in range(len(gameweek_array)):

		gameweek = gameweek_array[i]


		# declare an empty array
		g = []

		# for each manager in the league:
		for manager_code in manager_codes_list:

			# push a dict with:
			m = {}
			
			# manager code
			m['manager_code'] = manager_code
			# total league points
			m['league_points'] = output_data[manager_code]['league_points_running_total_array'][i]
			# total score
			m['total_score'] = output_data[manager_code]['fixture_score_running_total_array'][i]

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

	for key, val in temp_league_pos_data.items():

		manager_code = key

		output_data[manager_code]['league_position_array'] = val
		output_data[manager_code]['league_position_now'] = val[-1]

		def return_gameweeks_at_positon(pos):

			output = []

			for idx, v in enumerate(val):
				if v == pos:
					output.append(idx+1)

			return output


		output_data[manager_code]['league_position_high'] = {}
		output_data[manager_code]['league_position_high']['position'] = min(val)
		output_data[manager_code]['league_position_high']['gameweeks_at_position'] = return_gameweeks_at_positon(min(val))


		output_data[manager_code]['league_position_low'] = {}
		output_data[manager_code]['league_position_low']['position'] = max(val)
		output_data[manager_code]['league_position_low']['gameweeks_at_position'] = return_gameweeks_at_positon(max(val))


	return output_data



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
	database = return_load_json_file('2020_season_data.json')

	open_browser()


	gw_performance_data = return_scrape_and_compile_gw_performance_data()
	gw_performance_data = covid_fix(gw_performance_data)
	push_to_database_gw_performance_data(gw_performance_data)


	season_performance_data = return_compile_season_performance(gw_performance_data)
	push_to_database_season_performance_data(season_performance_data)


	datestamp = return_create_date_stamp()
	write_to_json_file('2020_season_data---'+datestamp, database)

	close_browser()

execute()