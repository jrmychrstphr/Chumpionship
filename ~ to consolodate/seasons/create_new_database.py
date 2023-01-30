import json
from pathlib import Path

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import operator

#####
def open_browser():
	global driver
	driver = webdriver.Firefox()
	print("Browser opened")

	
#####
def close_browser():
	driver.quit()
	print("Browser closed")

#####
def define_directory_name():
	input_verified = False

	while input_verified == False:

		name = input("Enter a name for this season's league (e.g. 2022): ")
		#check
		input_check = input('Are you sure? (Y): ')

		if str(input_check.upper()) == 'Y':
			input_verified == True
			break
		else:
			continue

	return name.strip().replace(" ", "_")

#####
def define_league_code():
	input_verified = False

	while input_verified == False:
		#define league code
		code = input("Enter league code: ")
		#check
		input_check = input('Are you sure? (Y): ')

		if str(input_check.upper()) == 'Y':
			input_verified == True
			break
		else:
			continue

	return code


#####
def load_page(league_code):

	print("Loading league page")

	league_url = 'https://fantasy.premierleague.com/leagues/' + league_code + '/new-entries/h'
	#league_url = 'https://fantasy.premierleague.com/leagues/' + league_code + '/standings/h'

	try:
		#open the webpage
		driver.get(league_url)
		
		#wait for the league table to appear in DOM
		element = WebDriverWait(driver, 10).until(
			EC.presence_of_element_located((By.CSS_SELECTOR, "table.Table-ziussd-1"))
		)
		

	except:
		#if the table is not found, display an error message
		print("Error loading league page: Table not found")
	
	else:
		#if the table is found, display successs message
		print("Success")

#####
def scrape():

	temp_array = []

	try:
		#create soup of page DOM
		soup = BeautifulSoup(driver.page_source, 'lxml')

		print(f"soup: {soup}")
		
		#filter to just league table
		league_table = soup.find_all('table' , class_='Table-ziussd-1')
		print(f"league_table: {league_table}")

		#find <a> tags in the league table
		anchors = league_table[0].find_all('a')
		print(f"anchors: {anchors}")

		for a in anchors:

			# if scraping league standing page (ie, after GW1)
			entry = {
				"manager_code" = a.get('href').split('/')[2],
				"team_name" = a.get_text(),
				"manager_name" = a.parent.contents[2].title()
			}

			print(entry)
			temp_array.append(entry)

	except:
		print('Error, unable to scrape page')

	else:
		return temp_array


#####
def create_dir(directory_name, input_array, league_code):

	folders = [directory_name, "email_assets"]

	directory_path = directory_name + '/database'

	# Create a subdirectory in the same directory as the py script
	p = Path(directory_path)
	try:
		p.mkdir(parents=True)
	except FileExistsError as exc:
		print(exc)


	#create dict of league info (league_code)
	league_info = {}
	league_info["league_code"] = league_code
	league_info["league_name"] = ""

	#save temp json of player info
	with open(directory_path + '/league_info.json', 'w') as json_file:
		json.dump(league_info, json_file, sort_keys=True, indent=4, separators=(',', ': '))

	#save temp json of player info
	with open(directory_path + '/temp_player_info.json', 'w') as json_file:
		json.dump(input_array, json_file, sort_keys=True, indent=4, separators=(',', ': '))


	#give user a chance to manually edit this file before proceeding
	input_verified = False

	while input_verified == False:
		#check
		print("File: 'player_info.json' created")
		print("Check and amend the file before continuing this process")
		input_check = input('Proceed? (Y): ')

		if str(input_check.upper()) == 'Y':
			input_verified == True
			break
		else:
			continue

	with open(directory_path + '/temp.json') as f:
		d = json.load(f)

		print(d)

		for x in d:

			folder_name = directory_path + '/' + x['manager_name'] + ' (' + x['manager_code'] + ')'

			# add a folder for each team
			p = Path(folder_name)
			try:
				p.mkdir(parents=True)
			except FileExistsError as exc:
				print(exc)

			#save json with player data in each 
			with open(folder_name+'/player_info.json', 'w') as json_file:
				json.dump(x, json_file, sort_keys=True, indent=4, separators=(',', ': '))

#####
def execute():

	open_browser()

	dir_name = define_directory_name()
	league_code = define_league_code()
	load_page(league_code)

	player_info = scrape()
	create_dir(dir_name, player_info, league_code)

	close_browser()


execute()
