"""

Takes data from fixture_scrape.json and compiles into:

* Compiles a full list of all weekly fixtures in ./data/fixture_list.json
* Compiles a full list of all weekly fixtures in ./builders/~ templates << this is used to build email assets


* Compiles each team's fixtures in ./data/[team directory]/fixture_list.json


"""

import os
import json
import random

database_dir = './data'

fixtures_dict = {}
manager_codes_list = []

# pull data from fixtures.json
with open(database_dir + "/fixture_scrape.json") as f:
	d = json.load(f)

	#populate fixtures_dict with empty lists 
	# for each week of the season 
	for manager_code, val in d.items():
		manager_codes_list.append(manager_code)

		for gameweek, opp_code in val.items():
			# if the gameweek is not in the dict, add it
			if gameweek not in fixtures_dict:
				fixtures_dict[gameweek] = []

	for gameweek in fixtures_dict:

		gw = int(gameweek.replace("GW", ""))

		m = manager_codes_list.copy()
		random.shuffle(m)


		while len(m) > 0:


			team_a = m[0]
			team_b = d[m[0]][gameweek]

			m.remove(team_a)				
			m.remove(team_b)
			
			fixture_obj = {}

			t = [team_a, team_b]
			random.shuffle(t)

			home_team = t[0]
			away_team = t[1]

			#check if fixture has already been added to the dict earlier in the season
			for g, fixtures in fixtures_dict.items():
				for fixture in fixtures:
					if (fixture['home_team'] == team_a and fixture['away_team'] == team_b):
						home_team = team_b
						away_team = team_a
					elif (fixture['away_team'] == team_a and fixture['home_team'] == team_b):	
						home_team = team_a
						away_team = team_b


			fixture_obj['home_team'] = home_team
			fixture_obj['away_team'] = away_team

			fixtures_dict[gameweek].append(fixture_obj)

			continue

# save a file with weekly fixtures in builders tempates
with open("./builders/~ templates/fixture-list.json", 'w') as f:
	json.dump(fixtures_dict, f, sort_keys=True, indent=4, separators=(',', ': '))

# save a file with weekly fixtures
with open(database_dir + "/fixture-list.json", 'w') as f:
	json.dump(fixtures_dict, f, sort_keys=True, indent=4, separators=(',', ': '))

	#use that file to generate a list each team's fixtures and save to their dir
	print(manager_codes_list)

	for manager_code in manager_codes_list:

		manager_fixture_dict = {}

		for gameweek, fixtures in fixtures_dict.items():

			manager_fixture_dict[gameweek] = {}

			for x in fixtures:
				if x['away_team'] == manager_code:
					manager_fixture_dict[gameweek]['opponent_code'] = x['home_team']
					manager_fixture_dict[gameweek]['status'] = 'away'
				elif x['home_team'] == manager_code:
					manager_fixture_dict[gameweek]['opponent_code'] = x['away_team']
					manager_fixture_dict[gameweek]['status'] = 'home'


		print(f'{manager_code}')
		#print(f'{manager_code}: {manager_fixture_dict}')


		for dirpath, dirnames, files in os.walk(database_dir):

			if str(manager_code) in str(dirpath):
				print(f'Found directory: {dirpath}')
				print(f'Saving fixtures to: {dirpath}/fixture-list.json')

				with open(dirpath + "/fixture-list.json", 'w') as f:
					json.dump(manager_fixture_dict, f, sort_keys=True, indent=4, separators=(',', ': '))


######
#Finally, check with user that everything is fine.

input_verified = False

while input_verified == False:

	input("Confirm that fixtures have successfully been compiled")
	input_check = input('All ok? (Y):')

	if str(input_check.upper()) == 'Y':
		input_verified == True
		break
	else:
		continue

#If yes, delete files from season folder:

files_to_delete = [
	"./data/fixtures_compiler.py",
	"./data/fixtures_scraper.py",
	"./data/fixture_scrape.json"
]

for x in files_to_delete:

	if os.path.exists(x):
		os.remove(x)
		print(f"File deleted: {x}")
	else: 
		print(f"File not found: {x}")





