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

	data_dict = {}
	database_dir = './database'

	# get league code from league_info.json
	with open(database_dir + "/league_info.json") as f:
		d = json.load(f)
		league_code = d['league_code']

	for dirpath, dirnames, files in os.walk(database_dir):
		print(f'Found directory: {dirpath}')

		if not dirpath == database_dir:

			for file_name in files:

				# open player_info.json
				if file_name == 'player_info.json':
					# get manager code from player_info.json
					with open(dirpath + "/" + file_name) as f:
						d = json.load(f)
						manager_code = d['manager_code']
						manager_name = d['manager_name']

			data_dict[manager_code] = {}

			# Build the url
			url = "https://fantasy.premierleague.com/leagues/" + league_code + "/matches/h?event=0&entry=" + manager_code

			try:
				print("Loading league fixtures page for ", manager_name)

				#open the page
				driver.get(url)

				#wait for the fixture table to appear in DOM
				element = WebDriverWait(driver, 30).until(
					EC.presence_of_element_located((By.CSS_SELECTOR, "table.Table-ziussd-1.MatchesTable__StyledMatchesTable-sc-1p0h4g1-0.fHBHIK.fwmEXa"))

				)


			except:
				#if the table is not found, display an error message
				print("Error - Data table not found")

			else:
				print("Success!")

				#create soup of DOM
				fixture_soup = BeautifulSoup(driver.page_source, 'lxml')

				#filter to the tr elements in the fixture table
				fixture_table_rows = fixture_soup.select("table.Table-ziussd-1.MatchesTable__StyledMatchesTable-sc-1p0h4g1-0.fHBHIK.fwmEXa tbody tr")

				#scrape FPL fixture list for each team in the database
				for row in fixture_table_rows:

					item_array = row.contents

					fixture_gameweek = "GW"+str("{0:0=2d}".format(int(item_array[0].get_text())))

					for x in item_array:

						if "MatchesEntry" in str(x):
							code = x.find('a').get('href').split('/')[2]
							#print(x.find('a').get('href').split('/')[2])

							# The DOM will have 2 matching hrefs for each fixture
							# The href that does not contain the current manager_code will be the opponent's code
							if code != manager_code:
								opponent_code = code

					data_dict[manager_code][fixture_gameweek] = opponent_code

				print(data_dict)

	##### WRITE TO DATABASE #####
	filename = database_dir + '/fixture_scrape.json'
	with open(filename, 'w') as f:
		print(f"Saving data to: {filename} ")
		json.dump(data_dict, f, sort_keys=True, indent=4, separators=(',', ': '))


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


#####
def execute():

	open_browser()

	accept_cookies()
	scrape()

	close_browser()


execute()
