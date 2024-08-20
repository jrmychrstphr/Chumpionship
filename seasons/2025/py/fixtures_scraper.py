# ============================================================
# This script scrapes all fixtures for the season and outputs 
# to one .json file called "temp_fixture_scrape.json"
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

	data_dict = {}
	data_dir_path = f"{Path(__file__).parent.parent}/data"

	# get league code from league_info.json
	with open(data_dir_path + "/league_info.json") as f:
		d = json.load(f)
		league_code = d["league_code"]

	for dirpath, dirnames, files in os.walk(data_dir_path):
		print(f"Found directory: {dirpath}")

		if not dirpath == data_dir_path:

			for file_name in files:

				# open player_info.json
				if file_name == "player_info.json":
					# get manager code from player_info.json
					with open(dirpath + "/" + file_name) as f:
						d = json.load(f)
						manager_code = d["fpl_code"]
						manager_name = d["manager_name"]

			data_dict[manager_code] = {}

			# Build the url
			url = "https://fantasy.premierleague.com/leagues/" + league_code + "/matches/h?event=0&entry=" + manager_code

			table_css_selector = "div.Layout__Main-sc-eg6k6r-1.eRnmvx table.Table-sc-ziussd-1.MatchesTable__StyledMatchesTable-sc-1p0h4g1-0.iPaulP.fwmEXa"

			try:
				print("Loading league fixtures page for ", manager_name)

				#open the page
				driver.get(url)

				#wait for the fixture table to appear in DOM
				WebDriverWait(driver, 30).until(
					EC.presence_of_element_located((By.CSS_SELECTOR, table_css_selector))
				)


			except:
				#if the table is not found, display an error message
				print("Error - data table not found")

			else:
				print("Success!")

				#create soup of DOM
				fixture_soup = BeautifulSoup(driver.page_source, "lxml")

				#filter to the tr elements in the fixture table
				fixture_table_rows = fixture_soup.select(table_css_selector + " tbody tr")

				#scrape FPL fixture list for each team in the database
				for row in fixture_table_rows:

					item_array = row.contents

					fixture_gameweek = str("{0:0=2d}".format(int(item_array[0].get_text())))

					for x in item_array:

						if "MatchesEntry" in str(x):
							code = x.find("a").get("href").split('/')[2]
							#print(x.find("a").get("href").split('/')[2])

							# The DOM will have 2 matching hrefs for each fixture
							# The href that does not contain the current manager_code will be the opponent's code
							if code != manager_code:
								opponent_code = code

					data_dict[manager_code][fixture_gameweek] = opponent_code

				print(data_dict)

	##### WRITE TO DATABASE #####
	filename = f"{Path(__file__).parent.parent}/data/temp_fixture_scrape.json"
	with open(filename, "w") as f:
		print(f"Saving data to: {filename} ")
		json.dump(data_dict, f, sort_keys=True, indent=4, separators=(",", ": "))



#####
def execute():

	open_browser()

	import cookies
	cookies.accept_cookies(driver)

	scrape()
	close_browser()


execute()