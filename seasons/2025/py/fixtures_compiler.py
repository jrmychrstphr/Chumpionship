# ============================================================
# This script:
# • Imports data from "temp_fixture_scrape.json"
# • Compiles a full week-by-week list of fixtures:
# 	 ../data/season_fixture_list.json
# • Compiles individual fixtures for each team:
# 	../data/[team directory]/fixture_list.json
# • It can also delete "temp_fixture_scrape.json" if desired
# ============================================================

import os
import json
import random

from pathlib import Path

fixtures_dict = {}
manager_code_list = []

data_dir_path = f"{Path(__file__).parent.parent}/data"
temp_file_location = f"{Path(__file__).parent.parent}/data/temp_fixture_scrape.json"
file_to_save_path = f"{Path(__file__).parent.parent}/data/season_fixture_list.json"



# pull data from fixtures.json
with open(temp_file_location) as f:
	d = json.load(f)

	#populate fixtures_dict with empty lists 
	# for each week of the season 
	for manager_code, val in d.items():
		manager_code_list.append(manager_code)

		for gameweek, opp_code in val.items():
			# if the gameweek is not in the dict, add it
			if gameweek not in fixtures_dict:
				fixtures_dict[gameweek] = []

	for gameweek in fixtures_dict:

		gw = int(gameweek)

		m = manager_code_list.copy()
		random.shuffle(m)

		while len(m) > 0:

			team_a = m[0]
			team_b = d[m[0]][str(gameweek)]

			m.remove(team_a)				
			m.remove(team_b)
			
			fixture_obj = {}

			t = [team_a, team_b]
			random.shuffle(t)

			home_team = t[0]
			away_team = t[1]

			#check if fixture has already been added to the dict earlier in the session
			for g, fixtures in fixtures_dict.items():
				for fixture in fixtures:
					if (fixture["home_team"] == team_a and fixture["away_team"] == team_b):
						home_team = team_b
						away_team = team_a
					elif (fixture["away_team"] == team_a and fixture["home_team"] == team_b):	
						home_team = team_a
						away_team = team_b


			fixture_obj["home_team"] = home_team
			fixture_obj["away_team"] = away_team

			fixtures_dict[str(gameweek)].append(fixture_obj)

			continue

# save full season fixture list...in the data directory
with open(file_to_save_path, "w") as f:
	json.dump(fixtures_dict, f, sort_keys=True, indent=4, separators=(",", ": "))

	#use that file to generate a list each team's fixtures and save to their dir
	for manager_code in manager_code_list:

		fixture_dict = {}

		for gameweek, fixtures in fixtures_dict.items():

			fixture_dict[str(gameweek)] = {}

			for x in fixtures:
				if x["away_team"] == manager_code:
					fixture_dict[str(gameweek)]["opponent_code"] = x["home_team"]
					fixture_dict[str(gameweek)]["status"] = "away"
				elif x["home_team"] == manager_code:
					fixture_dict[str(gameweek)]["opponent_code"] = x["away_team"]
					fixture_dict[str(gameweek)]["status"] = "home"

		print(f"{manager_code}")

		for dirpath, dirnames, files in os.walk(data_dir_path):

			if str(manager_code) in str(dirpath):
				print(f"Found directory: {dirpath}")
				print(f"Saving fixtures to: {dirpath}/fixture-list.json")

				with open(dirpath + "/fixture-list.json", "w") as f:
					json.dump(fixture_dict, f, sort_keys=True, indent=4, separators=(",", ": "))

######
#Finally, check with user that everything is fine.

input_check = input("Delete temp_fixtures_scrape.json? (Y):")

if str(input_check.upper()) == 'Y':
	# delete the temporary file
	if os.path.exists(temp_file_location):
		os.remove(temp_file_location)
		print(f"File: {temp_file_location} has been deleted")