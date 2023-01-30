import json
from pathlib import Path
import os

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
def scrape(league_code):

	temp_array = []
	codes_array = []

	# Load 'standings' page first
	print("Loading 'standings' page")

	league_url = 'https://fantasy.premierleague.com/leagues/' + league_code + '/standings/h'

	try:
		#open the webpage
		driver.get(league_url)
		
		#wait for the league table to appear in DOM
		element = WebDriverWait(driver, 10).until(
			EC.presence_of_element_located((By.CSS_SELECTOR, "table.Table-ziussd-1.hkwAOm"))
		)
		

	except:
		#if the table is not found, display an error message
		print("Err - Table not found")
	
	else:
		#if the table is found, display successs message
		print("Success")

		try:
			#create soup of page DOM
			soup = BeautifulSoup(driver.page_source, 'lxml')

			#print(f"soup: {soup}")
			
			#filter to just league table
			tables = soup.find_all('table' , class_='Table-ziussd-1')
			print(f"league_table: {tables}")

			#find <a> tags in the league table
			anchors = tables[0].find_all('a')
			print(f"anchors: {anchors}")

			if len(anchors) > 0 :
				for a in anchors:

					c = a.get('href').split('/')[2]

					if c not in codes_array: 

						# if scraping league standing page (ie, after GW1)

						entry = {
							"manager_code": c,
							"team_name": a.get_text(),
							"manager_name": a.parent.contents[2].title()
						}

						codes_array.append(c)

						temp_array.append(entry)

			else: print("No anchors found")

		except:
			print('Err - Unable to scrape page')


	

	##########

	# Load 'new-entries' page second 
	print("Loading 'new entries' page")

	league_url = 'https://fantasy.premierleague.com/leagues/' + league_code + '/new-entries/h'

	try:
		#open the webpage
		driver.get(league_url)
		
		#wait for the league table to appear in DOM
		element = WebDriverWait(driver, 10).until(
			EC.presence_of_element_located((By.CSS_SELECTOR, "table.Table-ziussd-1.hkwAOm"))
		)
		

	except:
		#if the table is not found, display an error message
		print("Err - Table not found")
	
	else:
		#if the table is found, display successs message
		print("Success")

		try:
			#create soup of page DOM
			soup = BeautifulSoup(driver.page_source, 'lxml')

			#print(f"soup: {soup}")
			
			#filter to just league table
			tables = soup.find_all('table' , class_='Table-ziussd-1')
			print(f"league_table: {tables}")

			#find <a> tags in the league table
			anchors = tables[0].find_all('a')
			print(f"anchors: {anchors}")

			if len(anchors) > 0 :

				for a in anchors:

					c = a.get('href').split('/')[2]

					if c not in codes_array: 

						entry = {
							"manager_code": c,
							"manager_name": a.get_text().title(),
							"team_name": a.parent.previous_sibling.get_text().title()
						}

						codes_array.append(c)

						#print(entry)
						temp_array.append(entry)

			else: print("No anchors found")



		except:
			print('Err - unable to scrape page')

		else:
			return temp_array


#####
def create_dir(directory_name, input_array, league_code):

	folders = ["assets", "builders", "data"]
	directory_path = directory_name + '/data'

	for x in folders:

		folder_name = directory_path + x

		# add a folder for each team
		p = Path(folder_name)
		try:
			p.mkdir(parents=True)
		except FileExistsError as exc:
			print(exc)


	#create dict of league info (league_code)
	league_info = {
		"league_code": league_code
		}

	#save json of player info
	with open(directory_path + '/league_info.json', 'w') as json_file:
		json.dump(league_info, json_file, sort_keys=True, indent=4, separators=(',', ': '))

	#save json of player info
	with open(directory_path + '/temp_player_info.json', 'w') as json_file:
		json.dump(input_array, json_file, sort_keys=True, indent=4, separators=(',', ': '))


	# pause to allow for manual edit of file before proceeding
	input_verified = False

	while input_verified == False:

		#check
		print("player_info.json created")
		print("Check and amend the file before continuing this process")
		input_check = input('Proceed? (Y): ')

		if str(input_check.upper()) == 'Y':
			input_verified == True
			break
		else:
			continue

	with open(directory_path + '/temp_player_info.json') as f:
		d = json.load(f)

		#print(d)

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

	# delete unneeded files
	if os.path.exists(directory_path + '/temp_player_info.json'):
  		os.remove(directory_path + '/temp_player_info.json')

#####
def execute():

	open_browser()

	league_code = define_league_code()
	player_info = scrape(league_code)

	print(player_info)

	dir_name = define_directory_name()
	create_dir(dir_name, player_info, league_code)

	close_browser()


execute()
