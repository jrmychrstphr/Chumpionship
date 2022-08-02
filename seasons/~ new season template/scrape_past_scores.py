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
driver = webdriver.Firefox()
print("Browser opened")



#####
league_code = input("Enter league code: ").strip()
league_url = 'https://fantasy.premierleague.com/leagues/' + league_code + '/new-entries/h'

try:
	
	print("Loading league page")
	#open the webpage
	driver.get(league_url)
	
	print("Locating data table")
	#wait for the league table to appear in DOM
	element = WebDriverWait(driver, 10).until(
		EC.presence_of_element_located((By.CSS_SELECTOR, "table.Table-ziussd-1"))
	)

except:
	#if the table is not found, display an error message
	print("Err -- Data table not found")

else:
	#if the table is found, display successs message
	print("Success -- Data table found")
	print("")

	manager_data = []

	try:
		#create soup of page DOM
		soup = BeautifulSoup(driver.page_source, 'lxml')
		#filter to just league table
		league_table = soup.find_all('table' , class_='Table-ziussd-1')
		#find <a> tags in the league table
		anchors = league_table[0].find_all('a')

		print("Scraping manager codes")
		#create a list of anager codes
		for a in anchors:

			d = {
				"manager_code": a.get('href').split('/')[2],
				"manager_name": a.get_text(),
				"past_seasons": []
			}

			manager_data.append(d)

	except:
		print('Err -- unable to scrape manager codes')

	else:
		print('Success -- manager codes scraped')
		print("")


if len(manager_data) == 0:
	print("Err -- no codes in list")
else:

	for x in manager_data:

		print(f"{x['manager_code']}")
		url = "https://fantasy.premierleague.com/entry/"+ x['manager_code'] +"/history"

		try:	
			#open the webpage
			print(f"Loading page ({x['manager_name']})")
			driver.get(url)
			print("Locating data table")
			#wait for the league table to appear in DOM
			element = WebDriverWait(driver, 10).until(
				EC.presence_of_element_located((By.CSS_SELECTOR, "table.Table-ziussd-1.hkwAOm"))
			)

		except:
			#if the table is not found, display an error message
			print("Err -- Data table not found")

		else:
			#if the table is found, display successs message
			print("Success -- Data table found")
			print("")

			# create soup of DOM
			history_page_soup = BeautifulSoup(driver.page_source, 'lxml')
			#locate 'This Season' table
			data_table = history_page_soup.find("h3", text="Previous Seasons")

			# move up the soup DOM until the table is found
			print(f"Searching for table")
			while len(data_table.select('table.Table-ziussd-1.hkwAOm')) == 0:
				data_table = data_table.parent	
			else:
				print(f"Table found")
				data_table = data_table
				data_table_rows = data_table.select('tbody tr')

				print(f"Scraping data")
				for row in data_table_rows:
					# scrape data
					row_data = row.contents

					d = {
						"season": str(row_data[0].get_text()),
						"points": int(row_data[1].get_text()),
						"rank": int(row_data[2].get_text())
					}

					print(d)

					x['past_seasons'].append(d)


print(manager_data)

#####
driver.quit()
print("Browser closed")


filename = "./builders/~ templates/past-seasons.json"
print(f"Saving data to {filename} ")

with open(filename, 'w') as f:
	json.dump(manager_data, f, sort_keys=True, indent=4, separators=(',', ': '))
