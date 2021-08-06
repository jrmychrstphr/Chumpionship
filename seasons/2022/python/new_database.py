∫import json
from pathlib import Path

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import operator


###############
# Set global variables #

global database
database = {}


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
# Define season name

def define_season():

	verification = False

	global season_name
	
	while verification == False:


		#Define season name
		season_name = input('Define a name for the season (e.g. Chumpionship 2020): ').replace(" ", "_").lower()

		#check
		input_check = input('Are you sure? (Y/N): ')

		if str(input_check.upper()) == 'Y':
			verification == True
			break
		else:
			continue


	season_name = season_name + '_database'


###############
# Define league info

def define_league_data():

	league_data = {}

	input_verified = False

	while input_verified == False:
		#define league code
		league_code = input("Enter the league's FPL code: ")
		#check
		input_check = input('Are you sure? (Y/N): ')

		if str(input_check.upper()) == 'Y':
			input_verified == True
			break
		else:
			continue

	#league_URL = 'https://fantasy.premierleague.com/leagues/' + league_code + '/standings/h'
	league_URL = 'https://fantasy.premierleague.com/leagues/' + league_code + '/new-entries/h'

	league_data['fpl_league_code'] = league_code
	league_data['fpl_league_url'] = league_URL
	league_data['entrant_id_list'] = []

	database['league_data'] = league_data



###############
# Load FPL League page

def load_league_page():

	league_URL = database['league_data']['fpl_league_url']


	try:
		#open the webpage
		driver.get(league_URL)
		
		#wait for the league table to appear in DOM
		element = WebDriverWait(driver, 10).until(
			#EC.presence_of_element_located((By.CSS_SELECTOR, "table.Table-ziussd-1.fHBHIK"))
			EC.presence_of_element_located((By.CSS_SELECTOR, "table.Table-ziussd-1"))
		)
		
	except:
		#if the table is not found, display an error message
		print("Error: League table element not found :(")
	
	else:
		#if the table is found, display successs message
		print("Success: League table element found :D")


def scrape_manager_data_from_league_page():

	try:

		#create soup of page DOM
		soup = BeautifulSoup(driver.page_source, 'lxml')
		
		#filter to just league table
		league_table = soup.find_all('table' , class_='Table-ziussd-1')
		#print(league_table)

		#find <a> tags in the league table
		anchors = league_table[0].find_all('a')
		#anchors = league_table[1].find_all('a')

		global temp_players
		temp_players = []

		for anchor in anchors:

			team_name = anchor.parent.parent.contents[0].get_text()	#team_name
			manager_fullname = anchor.get_text()	#manager_fullname
			fpl_code = anchor.get('href').split('/')[2]	#fpl_code

			entry = [fpl_code, team_name, manager_fullname]

			print(entry)
			temp_players.append(entry)

	except:
		print('Error, unable to scrape page')

	else:
		temp_players = check_and_change(temp_players)
		return temp_players


###############
# Manually change an array and return the result

def check_and_change(input_array):


	progress_check = False
	breadcrumb_array = []
	
	while progress_check == False:
	
		#reset temp array
		temp_array = input_array

		#navigate database_array seleced via breadcrumbs
		if len(breadcrumb_array) > 0:

			for x in breadcrumb_array:
				temp_array = temp_array[x]

		#if multiple options exist, ask to chose an option, update breadcrumbs, then restart loop
		if isinstance(temp_array, list):

			print('')

			#print indexed menu of the current array
			for idx, x in enumerate(temp_array):
				print(idx, x)

			print('')
			print('Is this data correct?')
			print('Yes:: Enter "Y"')
			print('NO::  Enter the number of the item you want to change')
			user_input = input()

			#if the information shown is correct, remove the last item from breadcrumbs (if it exists) and restart the loop
			if str(user_input.upper()) == 'Y':

				if len(breadcrumb_array) > 0:
					#remove last breadcrumb
					del breadcrumb_array[-1]
					#restart the loop
					continue
				else:
					#break the loop
					progress_check = True
					break

			#if the input is all numbers
			elif user_input.isnumeric():

				try:
					breadcrumb_array.append(int(user_input))
					print('You entered: ' + user_input)
					continue

				except:
					print('Error: 1')

			else:
				print('Error: 2')

		#if only 1 option exists in current selection, manually update that item
		else:

			print('')
			print('Editing: ', temp_array)
			user_update = input('Enter the new value: ')

			#if numeric, convert type
			if user_update.isnumeric():
				if '.' in user_update:
					print('converted to float')
					user_update = float(user_update)
				else:
					print('converted to integer')
					user_update = int(user_update)
			#if input is empty, do not update and move back one level		
			elif len(user_update) == 0:
				#remove last breadcrumb
				del breadcrumb_array[-1]
				#restart the loop
				continue

			##update original array object with user input

			#create a temporary copy of breadcrumbs
			temp_breadcumb = breadcrumb_array

			while len(temp_breadcumb) > 0:
				#print('breadcrumbs: ', temp_breadcumb)
				
				#reset temp_array
				temp_array = input_array

				for idx, x in enumerate(temp_breadcumb):

					if idx != len(temp_breadcumb)-1:

						#loop through breadcrumbs to traverse array to parent of update
						temp_array = temp_array[x]

					else:
						#update parent
						temp_array[x] = user_update

						#assign update to next level up
						user_update = temp_array

						#remove the last breadcrumb
						del temp_breadcumb[-1]

			else: 
				temp_array = user_update

			#update the array
			input_array = temp_array


	output = sorted(input_array,key=lambda x: x[2])
	return output


##############
# Scrapes previous season scores #
# stores them to player_data > fpl_history #
def scrape_and_return_fpl_history(manager_code):

	manager_URL = 'https://fantasy.premierleague.com/entry/'+manager_code+'/history'

	try:
		#open the webpage
		driver.get(manager_URL)
		
		#wait for the league table to appear in DOM
		element = WebDriverWait(driver, 10).until(
			EC.presence_of_element_located((By.CSS_SELECTOR, "table.Table-ziussd-1"))
			#EC.presence_of_element_located((By.CSS_SELECTOR, "table.Table-ziussd-1.fHBHIK"))
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
		while len(element.select('.Table-ziussd-1')) == 0:
			element = element.parent
		else:
			prev_seasons_rows = element.select('.Table-ziussd-1 tbody tr')

			fpl_history = {}

			for row in prev_seasons_rows:
				row_contents_array = row.contents

				season = row_contents_array[0].get_text().replace("/", "_")
				score = row_contents_array[1].get_text()

				fpl_history[season] = score

			return fpl_history


###############
# push player info to database

def initialise_player_data(input_array):

	database['player_data'] = {}


	for idx, x in enumerate(input_array):

		#print(idx, x)

		manager_info = {}

		manager_info['fpl_code'] = x[0]
		manager_code = manager_info['fpl_code']

		manager_info['team_name'] = x[1]
		manager_info['manager_fullname'] = x[2]
		manager_info['fpl_history'] = scrape_and_return_fpl_history(manager_code)

		database['player_data'][manager_code] = {}	
		database['player_data'][manager_code]['manager_info'] = manager_info

		#database['player_data'][manager_code]['gw_performance'] = {}
		#database['player_data'][manager_code]['fixtures'] = {}

		database['league_data']['entrant_id_list'].append(manager_code)


###############
# write data to json
def write_to_json_file(filename, data):
    with open(filename + '.json', 'w') as json_file:
        json.dump(data, json_file, sort_keys=True, indent=4, separators=(',', ': '))


###############
###############


###############
# log in to the FPL site
def log_in():

	log_in_URL = "https://fantasy.premierleague.com/"

	try:
		#open the webpage
		driver.get(log_in_URL)
		
		#wait for the log-in form to appear in DOM
		element = WebDriverWait(driver, 10).until(
			#EC.presence_of_element_located((By.CSS_SELECTOR, "table.Table-ziussd-1.fHBHIK"))
			EC.presence_of_element_located((By.CSS_SELECTOR, "form.Login__LoginForm-sc-1dpiyoc-4"))
		)
		
	except:
		#if the table is not found, display an error message
		print("Error: Login form not found :(")
	
	else:
		#if the table is found, display successs message
		print("Success: Login form found :D")

		try:
			driver.find_element_by_id('loginUsername').send_keys("jrmychrstphr@gmail.com")
			pw = driver.find_element_by_id('loginPassword')
			pw.send_keys("givemeaccess")

			pw.submit()
			print("Success: Login form submitted :D")

		except:
			#if the table is not found, display an error message
			print("Error: Failed to submit form :(")





def execute():

	define_season()
	#print(database)

	open_browser()

	#log_in()

	define_league_data()
	#print(database)

	load_league_page()

	initialise_player_data(scrape_manager_data_from_league_page())
	#print(database)

	close_browser()

	write_to_json_file(season_name + ' - new', database)


execute()
