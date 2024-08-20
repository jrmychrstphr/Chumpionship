# ============================================================
# This script imports data from the '../data' directory tree
# calculates weekly fixture results, weekly score ranks, 
# weekly league positions. That info is then compiled into a 
# single .json file saved called '../data/database.json' which 
# can be used to build visualisations
# ============================================================


import os
import json

from pathlib import Path


#create empty dict to store data
database = {}
third_pass_dict = {}

data_dir_path = f"{Path(__file__).parent.parent}/data"

for item in os.listdir(data_dir_path):
	item_filepath = data_dir_path + "/" + item
	
	#for each subfolder (ie, for each team)...
	if os.path.isdir(item_filepath):

		print(f"{item_filepath}")

		data_dict = {}
		list_of_subfolder_contents = os.listdir(item_filepath)
		list_of_subfolder_contents.sort()

		# Create a list of existing gameweeks
		existing_gameweeks = [x.replace("GW", "").replace(".json", "") for x in list_of_subfolder_contents if x.startswith("GW")]

		#pull info from 'player_info.json'
		if "player_info.json" in list_of_subfolder_contents:
			with open(item_filepath + "/player_info.json") as f:
				d = json.load(f)
				manager_code = d["fpl_code"]
				manager_name = d["manager_name"]
				team_name = d['team_name']
		else: 
			print("Err - 'player_info.json' not found")
			exit()


		# pull info from 'fixture-list.json'
		if "fixture-list.json" in list_of_subfolder_contents:
			with open(item_filepath + "/fixture-list.json") as f:
				d = json.load(f)
				fixture_opponent_array = [val.get("opponent_code") for val in d.values()]
		else: 
			print("Err - 'fixture-list.json' not found")
			exit()

		#print(f"ex: {existing_gameweeks}")
		#print(f"fix: {fixture_opponent_array}")


		#create empty lists for the data to go in
		database[manager_code] = {

			"fpl_code": str(manager_code),
			"manager_name": str(manager_name),
			"team_name": str(team_name),

			"fixture_score_array": [],
			"total_score_array": [],
			"fixture_opponent_array": fixture_opponent_array,
			"chip_played_array": [],

			"transfers_made_array": [],
			#"transfered_in_array": [],
			#"transfered_out_array": [],

			"captains_array": [],
			"captains_points_array": [],

		}


		for filename in [x for x in sorted(list_of_subfolder_contents) if x.startswith("GW")]:
			#print(f"file {filename}")
			# pull data from files
			with open(item_filepath + "/" + filename) as f:
				d = json.load(f)

				if "fixture_score" in d:
					database[manager_code]["fixture_score_array"].append(d["fixture_score"])

				if "overall_total_points" in d:
					database[manager_code]["total_score_array"].append(d["overall_total_points"])

				if "chip_played" in d:
					database[manager_code]["chip_played_array"].append(d["chip_played"])

				if "transfers_made" in d:
					database[manager_code]["transfers_made_array"].append(d["transfers_made"])

				"""
				if "transfered_in" in d:
					database[manager_code]["transfered_in_array"].append(d["transfered_in"])

				if "transfered_out" in d:
					database[manager_code]["transfered_out_array"].append(d["transfered_out"])
				"""

				if "captain_name" in d:
					database[manager_code]["captains_array"].append(d["captain_name"])

				if "captain_score" in d:
					database[manager_code]["captains_points_array"].append(d["captain_score"])
					

		print(f"{manager_name}")
		print(f"{database[manager_code]}")

# second pass (calculate fixture results, league points)
for manager_code in database:

	print(f"{manager_code}")

	d = database.copy()

	# add keys to database 
	database[manager_code].update({"fixture_result_array": []})
	database[manager_code].update({"league_points_array": []})
	database[manager_code].update({"total_league_points_array": []})
	database[manager_code].update({"fixture_margin_array": []})

	# temporary lists
	fixture_points_array = []
	fixture_margin_array = []

	#for count, value in enumerate(d[manager_code]["fixture_score_array"]):
	for count, gameweek in enumerate(sorted(existing_gameweeks)):

		# print(f"count: {count}")
		# print(f"gameweek: {gameweek}")

		score = database[manager_code]["fixture_score_array"][count]
		# print(f"score: {score}")
		opponent_score = database[d[manager_code]["fixture_opponent_array"][count]]["fixture_score_array"][count]
		fixture_margin = float(score) - float(opponent_score)


		#calculate fixture result
		if fixture_margin > 0:
			database[manager_code]["fixture_result_array"].append("win")
			database[manager_code]["league_points_array"].append(3)
		elif fixture_margin < 0:
			database[manager_code]["fixture_result_array"].append("loss")
			database[manager_code]["league_points_array"].append(0)
		elif fixture_margin == 0:
			database[manager_code]["fixture_result_array"].append("draw")
			database[manager_code]["league_points_array"].append(1)
		else:
			fixture_result = "error"
			fixture_points_array.append("error")
			print(f"Error calculating result: {d[manager_code]['manager_name']}, GW{gameweek}")
			exit()

		database[manager_code]["total_league_points_array"].append(sum(database[manager_code]["league_points_array"]))
		database[manager_code]["fixture_margin_array"].append(float(fixture_margin))

		# push data to third_pass_dict for calculating league position later
		if gameweek not in third_pass_dict:
			third_pass_dict[gameweek] = []

		temp_obj = {
			"manager_code": manager_code,
			"league_points":d[manager_code]["total_league_points_array"][count],
			"total_score": d[manager_code]["total_score_array"][count],
			"fixture_score": d[manager_code]["fixture_score_array"][count]
		}

		third_pass_dict[gameweek].append(temp_obj)

#print(third_pass_dict)

# third pass (calculate league position, gw score ranks)
for gameweek, value in third_pass_dict.items():

	d = sorted(value.copy(), key = lambda x: (x["league_points"], x["total_score"]), reverse=True)
	for idx, val in enumerate(d):

		manager_code = val["manager_code"]

		if idx > 0:
			# if league points and total score  == the previous entry in the array,
			if d[idx]["league_points"] == d[idx-1]["league_points"] and d[idx]["total_score"] == d[idx-1]["total_score"]:
				# the position is the same as the previous entry
				pos = pos
			#else, the position is determined by the item's position in the sorted list
			else:
				pos = idx+1
		#the league pos for the first item in the sorted list will always be 1
		else:
			pos = idx+1

		if "league_position_array" not in database[manager_code]:
			database[manager_code].update({"league_position_array": []})

		database[manager_code]["league_position_array"].append(int(pos))

	
	d = sorted(value.copy(), key = lambda x: (x["fixture_score"]), reverse=True)
	for idx, val in enumerate(d):

		manager_code = val["manager_code"]

		if idx > 0:
			# if fixture_score  == the previous entry in the array,
			if d[idx]["fixture_score"] == d[idx-1]["fixture_score"]:
				# the position is the same as the previous entry
				score_rank = score_rank
			#else, the position is determined by the item's position in the sorted list
			else:
				score_rank = idx+1
		#the league pos for the first item in the sorted list will always be 1
		else:
			score_rank = idx+1

		if "fixture_score_rank_array" not in database[manager_code]:
			database[manager_code].update({"fixture_score_rank_array": []})

		database[manager_code]["fixture_score_rank_array"].append(int(score_rank))


#print(database)

# save database in the data directory
with open(f"{Path(__file__).parent.parent}/data/database.json", "w") as f:
	json.dump(database, f, sort_keys=True, indent=4, separators=(",", ": "))