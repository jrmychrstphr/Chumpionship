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

import shutil

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
		input_check = input("Are you sure? (Y): ")

		if str(input_check.upper()) == "Y":
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
		input_check = input("Are you sure? (Y): ")

		if str(input_check.upper()) == "Y":
			input_verified == True
			break
		else:
			continue

	return code



#####
def scrape(league_code):

	import fpl_accept_cookies
	fpl_accept_cookies.accept_cookies(driver)


	temp_array = []
	codes_array = []

	league_standings_url = "https://fantasy.premierleague.com/leagues/" + str(league_code) + "/standings/h"
	league_newentries_url = "https://fantasy.premierleague.com/leagues/" + str(league_code) + "/new-entries/h"

	table_css_selector = "table.Table-sc-ziussd-1.iPaulP" 

	# Load 'standings' page first
	print("Loading 'standings' page")

	try:
		#open the webpage
		driver.get(league_standings_url)

		#wait for the league table to appear in DOM
		element = WebDriverWait(driver, 10).until(
			EC.presence_of_element_located((By.CSS_SELECTOR, table_css_selector))
		)
		

	except:
		#if the table is not found, display an error message
		print("Err - Table not found")
	
	else:
		#if the table is found, display successs message
		print("Success")

		try:
			#create soup of page DOM
			soup = BeautifulSoup(driver.page_source, "lxml")

			print(f"soup made")
			#print(f"soup: {soup}")
			
			#filter to just league table
			tables = soup.find_all("table" , class_="Table-sc-ziussd-1") 
			print(f"league table found")
			#print(f"league_table: {tables}")

			#find <a> tags in the league table
			anchors = tables[0].find_all("a")
			print(f"anchors found")
			#print(f"anchors: {anchors}")

			if len(anchors) > 0 :
				for a in anchors:

					c = a.get("href").split("/")[2]

					if c not in codes_array: 

						# if scraping league standing page (ie, after GW1)

						entry = {
							"fpl_code": c,
							"team_name": a.get_text(),
							"manager_name": a.parent.contents[2].title()
						}

						codes_array.append(c)

						temp_array.append(entry)

			else: print("No anchors found")

		except:
			print("Err - Unable to scrape page")


	

	##########

	# Load 'new-entries' page second 
	print("Loading 'new entries' page")

	try:
		#open the webpage
		driver.get(league_newentries_url)
		
		#wait for the  table to appear in DOM
		element = WebDriverWait(driver, 10).until(
			EC.presence_of_element_located((By.CSS_SELECTOR, table_css_selector))
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

			#locate table h3 text element 'New entries'
			new_entries_table = soup.find("h3", text="New entries")

			# move up the soup DOM until the table is found
			while len(new_entries_table.select(table_css_selector)) == 0:
				new_entries_table = new_entries_table.parent
				print("moving up the DOM")
			else:
				new_entries_table = new_entries_table
				new_entries_table_rows = new_entries_table.select(table_css_selector + ' tbody tr')
				print("table located")
			
			if len(new_entries_table_rows) > 0:

				print("info found")

				for row in new_entries_table_rows:
					row_contents_array = row.contents

					team_name = str(row_contents_array[0].get_text().title())
					manager_name = str(row_contents_array[1].get_text().title())
					fpl_code = str(row_contents_array[1].find('a').get('href').split('/')[2])

					info = {
						"fpl_code": fpl_code,
						"manager_name": manager_name,
						"team_name": team_name
					}

					#codes_array.append(fpl_code)

					print(info)
					temp_array.append(info)

			else: print("No info found")

		except:
			print("Err - unable to scrape page")

		else:
			return temp_array


#####
def create_dir(directory_name, input_array, league_code):

	directory_path = directory_name + '/data'

	#create dict of league info (league_code)
	league_info = {
		"league_code": league_code
		}

	#copy the directory template
	source_dir = "seasons/~ new season template"
	destination_dir = "seasons/" + directory_name
	shutil.copytree(source_dir, destination_dir)


	#save json of league info
	with open(destination_dir + '/data/league_info.json', 'w') as json_file:
		json.dump(league_info, json_file, sort_keys=True, indent=4, separators=(',', ': '))

	#save json of player info
	with open(destination_dir + '/data/temp_player_info.json', 'w') as json_file:
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

	with open(destination_dir + '/data/temp_player_info.json') as f:
		d = json.load(f)

		#print(d)

		for x in d:

			print(x)

			folder_name = destination_dir + '/data/' + x['manager_name'] + ' (' + x['fpl_code'] + ')'

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
	if os.path.exists(destination_dir + '/data/temp_player_info.json'):
  		os.remove(destination_dir + '/data/temp_player_info.json')


####
# Copy files to the newly created folder:
#	./fixtures_compiler.py >> move full-season fixtures.json export to ./buliders/~ template files/
#	./fixtures_scraper.py
#	./purge_gameweekdata.py
#	./data_scraper.py
#	./data_compiler.py >> export database.josn to ./buliders/~ template files/


#####
def execute():

	open_browser()

	league_code = define_league_code()
	player_info = scrape(league_code)

	dir_name = define_directory_name()
	create_dir(dir_name, player_info, league_code)

	close_browser()


execute()
