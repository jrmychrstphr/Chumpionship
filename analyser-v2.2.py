# Need to add:
# + Most popular captain choice

import json
from collections import Counter

# load database
season_dir = './seasons/2024'	#edit this to target different seasons

database_path = season_dir + '/data/database.json'
fixtures_path = season_dir + '/data/season_fixture_list.json'

with open(database_path) as f:
	d_data = json.load(f)

with open(fixtures_path) as f:
	d_fixtures = json.load(f)

# useful functions
def ord(n):
    return str(n)+("th" if 4<=n%100<=20 else {1:"st",2:"nd",3:"rd"}.get(n%10, "th"))

def comma_format(n):
 	 return ("{:,}".format(n))

def format_two_digit(n):
	return str("{0:0=2d}".format(int(n)))

def written_number(n):
	numbers = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
	if int(n) < 10:
		return str(numbers[int(n)])
	else:
		return str(n)

"""

GW general:
– Total combined fixture score
– – Highest score of the snz?
– – Highest score in 5+ wks? 
– Breakdown of chips used
– Total transfers made

"""

#build a gw-by-gw dataset
d_gwdata = {}

for key, val in d_data.items():

	#print(f"key: {key}, val: {val}")

	#combined_fixture_scores
	if "combined_fixture_scores" not in d_gwdata:
		d_gwdata["combined_fixture_scores"] = val['fixture_score_array'].copy()
	else:
		#if the list already exists, add together the scores
		for idx, v in enumerate(val['fixture_score_array']):
			d_gwdata["combined_fixture_scores"][idx]+=v

	#all_fixture_scores
	if "all_fixture_scores" not in d_gwdata:
		d_gwdata["all_fixture_scores"] = [[x] for x in val['fixture_score_array']]
	else:
		#if the list already exists, add together the scores
		for idx, v in enumerate(val['fixture_score_array']):
			d_gwdata["all_fixture_scores"][idx].append(v)

	#transfers_made
	if "transfers_made" not in d_gwdata:
		d_gwdata["transfers_made"] = val['transfers_made_array'].copy()
	else:
		#if the list already exists, add together the scores
		for idx, v in enumerate(val['transfers_made_array']):
			d_gwdata["transfers_made"][idx]+=v

	#chips_played
	for idx, v in enumerate(val['chip_played_array']):

		if "chips_played" not in d_gwdata:
			d_gwdata["chips_played"] = []

		#print(v)

		if len(d_gwdata["chips_played"]) < idx+1:
			new_list = []
			d_gwdata["chips_played"].append(new_list)
		
		if v.lower() != "none":
			chip = str(v.lower())
			fpl_code = val["fpl_code"]

			t = tuple((chip,fpl_code))

			d_gwdata["chips_played"][idx].append(t)

#print(d_gwdata)

def gw_stats(gw):

	#stop if the dataset is shorter that the requested gw
	if len(d_gwdata["combined_fixture_scores"]) < gw:
		print("Gameweek "+ str(gw) +" has not yet been played")
		return


	#create an empty list to store statements in
	print_statements = []

	###############
	#scores
	scores = d_gwdata["combined_fixture_scores"][:(gw)]
	gameweek_score = scores[-1]
	scores_sorted = sorted(scores, reverse=True)
	score_highest_in = 0

	for idx, x in enumerate(reversed(scores)):
		if idx > 0 and x >= gameweek_score:
			score_highest_in = idx
			break
	
	score_rank = scores_sorted.index(gameweek_score)+1

	#build the statement
	#top score in gw 1 or after GW4
	if score_rank == 1 and gw > 4 or gw == 1:
		message = "Round " + str(gw) + " was the highest-scoring week of the season so far,"\
			" with a combined haul of " +\
			str(comma_format(d_gwdata["combined_fixture_scores"][int(gw-1)]))
	
	#lowest score after GW4
	elif score_rank == gw and gw > 4:
		message = "Round " + str(gw) + " was the lowest-scoring week of the season so far,"\
			" with a combined total of just " +\
			str(comma_format(d_gwdata["combined_fixture_scores"][int(gw-1)]))

	#top-five score after GW9
	elif score_rank <= 5 and gw > 9:
		message = "Round " + str(gw) + " was the " + ord(score_rank) +\
		"-highest-scoring week of the season so far, with a combined total of " +\
			str(comma_format(d_gwdata["combined_fixture_scores"][int(gw-1)]))

	#bottom-five score after GW9
	elif score_rank >= (gw-4) and gw > 9:
		message = "Round " + str(gw) + " was the " + ord(gw-score_rank+1) +\
		"-lowest-scoring week of the season so far, with a combined total of only " +\
			str(comma_format(d_gwdata["combined_fixture_scores"][int(gw-1)]))

	#any other score
	else:
		message = "Round " + str(gw) + " saw Chumpionship teams score a combined total of " +\
			str(comma_format(d_gwdata["combined_fixture_scores"][int(gw-1)])) +\
			" points"

	#difference in score to last GW
	if gw > 1:
		score_diff = scores[-1] - scores[-2]
		if score_diff == 0:
			message += " – the same score as last time out"
		if score_diff > 0:
			message += " – " + str(comma_format(score_diff)) + " more than last time out"
		if score_diff < 0:
			message += " – " + str(comma_format(score_diff*-1)) + " fewer than last time out"

	#if score is highest in over 2 weeks, after GW4
	if score_highest_in > 2 and gw > 4:
		message += ", and the highest combined score for " + str(score_highest_in) + " Weeks"
	
	#add the average score
	# print(d_gwdata["all_fixture_scores"][int(gw-1)])
	# print(d_gwdata["all_fixture_scores"])
	avg = sum(d_gwdata["all_fixture_scores"][int(gw-1)])/len(d_gwdata["all_fixture_scores"][int(gw-1)])
	message += ". The average score was " + str(comma_format(round(avg, 2)))

	#add message to statements list
	if len(message) > 0:
		print_statements.append(message)
		message = ""	#reset

	###############
	#transfers_made
	transfers = d_gwdata["transfers_made"][:(gw)]
	#print(transfers)
	gameweek_transfers = transfers[-1]
	transfers_sorted = sorted(transfers, reverse=True)
	#print(transfers_sorted)
	transfers_rank = transfers_sorted.index(gameweek_transfers)+1

	#build the statement
	if  gw > 4 and transfers_rank == 1:
		message += "The busiest transfer window of the campaign to date saw " +\
			str(comma_format(gameweek_transfers)) + " changes to Chumpionship rosters ahead of the "\
			"GW" + str(gw) + " deadline"
		
	elif gameweek_transfers > 0:
		message += "Chumpionship gaffers combined to make " + str(comma_format(gameweek_transfers)) +\
		" transfers ahead of the GW" + str(gw) + " deadline"

	else: 
		message += "No transfers were made ahead of GW" + str(gw)

	#add message to statements list
	if len(message) > 0:
		print_statements.append(message)
		message = ""	#reset


	###############
	#No chips
	if len(d_gwdata["chips_played"][gw-1]) == 0:
		message += "No chips were played"
	
	#chips played
	else:

		dict_chips = {}

		for idx, val in enumerate(d_gwdata["chips_played"][gw-1]):
			#convert to an itemised dict
			if str(val[0]) not in dict_chips:
				dict_chips[str(val[0])] = 1
			else:
				dict_chips[str(val[0])] += 1

		#sort the result, largest first
		sorted_dict_chips = sorted(dict_chips.items(), key=lambda x:(-x[1], x[0]))

		if len(sorted_dict_chips) == 1 and sorted_dict_chips[0][1] == 1:
			message += str(written_number(sorted_dict_chips[0][1])).title() + " team played a " + str(sorted_dict_chips[0][0]).title() + " chip"
		
		elif len(sorted_dict_chips) == 1:
			message += str(written_number(sorted_dict_chips[0][1])).title() + " teams played a " + str(sorted_dict_chips[0][0]).title() + " chip"
		
		else:
			message += str(written_number(len(d_gwdata["chips_played"][gw-1]))).title() + " chips were played: "
			
			for idx, val in enumerate(sorted_dict_chips):
				if val[1] == 1:
					message += str(written_number(int(val[1]))) + " " + str(val[0]).title()
				else: 
					message += str(written_number(int(val[1]))) + " " + str(val[0]).title() + "s"

				if idx == len(sorted_dict_chips)-2:
					message += ", and "
				if idx < len(sorted_dict_chips)-2:
					message += ", "

	
	#add message to statements list
	if len(message) > 0:
		print_statements.append(message)
		message = ""	#reset


	for x in print_statements:
		print(x)


"""
Fixture specific:

Scores
– Top scoring team that GW? *
– Lowest scoring team that GW? *
– Personal best scores? *
– Personal lowest scores? *
- Highest single score of the season? *
- Lowest single score of the season? *

- How many teams set pb/pw scores that gw? <<<

Margins
– Personal biggest win / loss? *
– Biggest winning margin that GW? *
- Biggest winning margin of the season? *

- How many teams set pb/w margins that GW? <<<


Streaks
– Extended a win streak
– Extended a winless (D/L) streak
– Ended a win streak
– Ended a winless (D/L) streak
– Personal longest win streak?
– Personal longest winless streak?
– Season longest win streak?
– Season longest winless streak?

League positions
- Topped the league
-- Topped the league for the nth-time
-- Returned to 1st place after x weeks
-- Extended a stint in 1st place

- Top 4
-- Entered the Top 4 for the nth time
-- Returned to Top 4 after x weeks
-- Extended a stint in Top 4 (5wk or more?)
-- Fell out of the top 4 after n weeks

- Bottom three
-- Entered Bottom three for the nth time
-- Extended stint in bottom three
-- Left bottom three after x weeks
-- nth time in bottom three


- Team closed gap to top to under 5pts
- Bottom three closed gap to 17th to under 5pts
- Bottom three beat top-four

Chips
- Played a chip
- Value of chip
(Rank in chip return, eg: X played a BB, got Xpts -- the nth-best return on a BB this season)

"""

d_fxdata = {}

for key, val in d_data.items():

	#print(val)

	#fixture scores
	if "fixture_scores" not in d_fxdata:
		d_fxdata["fixture_scores"] = []

		for idx, v in enumerate(val["fixture_score_array"]):
			d_fxdata["fixture_scores"].append([])

	for idx, v in enumerate(val["fixture_score_array"]):
		d_fxdata["fixture_scores"][idx].append(v)

	#fixture margins
	if "fixture_margins" not in d_fxdata:
		d_fxdata["fixture_margins"] = []

		for idx, v in enumerate(val["fixture_margin_array"]):
			d_fxdata["fixture_margins"].append([])

	for idx, v in enumerate(val["fixture_margin_array"]):
		d_fxdata["fixture_margins"][idx].append(v)

#print(d_fxdata)

def fx_stats(gw):

	fx_list = []
	f

	gameweek_fixturelist = d_fixtures[str(format_two_digit(gw))]
		
	#for each fixture in the gameweek...
	for fix in gameweek_fixturelist:
		
		fx_dict = {}

		#for each team in the fixture..
		for key, val in fix.items():
			
			fx_dict[str(key)] = {
				"fpl_code": str(val),
				"team_name": str(d_data[str(val)]["team_name"]),
				#"manager_name": str(d_data[str(val)]["manager_name"]),
				#"manager_firstname": str(d_data[str(val)]["manager_name"]).split()[0],
				#"manager_surname": str(d_data[str(val)]["manager_name"]).split()[1],

				#array of all scores to date, to assess highest/lowest since...
				"fixture_score_array": d_data[str(val)]["fixture_score_array"][:int(gw)],
				"fixture_score": d_data[str(val)]["fixture_score_array"][int(gw-1)],

				#array of all score ranks to date, to assess highest/lowest since...
				"fixture_score_rank_array": d_data[str(val)]["fixture_score_rank_array"][:int(gw)],
				"fixture_score_rank": d_data[str(val)]["fixture_score_rank_array"][int(gw-1)],

				#array of all score margins to date, to assess highest/lowest since...
				"fixture_margin_array": d_data[str(val)]["fixture_margin_array"][:int(gw)],
				"fixture_margin": d_data[str(val)]["fixture_margin_array"][int(gw-1)],

				#array of all results (win, loss, draw)...
				"fixture_result_array": d_data[str(val)]["fixture_result_array"][:int(gw)],
				"fixture_result": d_data[str(val)]["fixture_result_array"][int(gw-1)],

			}

			if "fix_combined_score" not in fx_dict:
				fx_dict["fix_combined_score"] = float(fx_dict[str(key)]["fixture_score"])
			else:
				fx_dict["fix_combined_score"] += float(fx_dict[str(key)]["fixture_score"])

		fx_list.append(fx_dict)

	# sort the list by home team name
	sorted_fx_list = sorted(fx_list, key=lambda x: x["home_team"]["team_name"])

	#devise a better, score-based ordering system later

	print_statements = []

	def stats(team):

		stats = []

		fixture_score = fix[team]["fixture_score"]

		#Top score on the season
		if fixture_score == season_max_score and gw > 1:
			#if multiple teams set a new season high-score		
			if season_max_score_count > 1 and gameweek_max_score_count > 1 and season_max_score_count == gameweek_max_score_count:
				msg = "Was one of " + str(gameweek_max_score_count) + \
				"teams to set a new season-high score in GW" + str(gw) + " with a haul of " + str(fixture_score) + "pts"
			
			#if multiple teams equalled a previously set season high-score		
			elif season_max_score_count > 1 and gameweek_max_score_count > 1:
				msg = "Was one of " + str(gameweek_max_score_count) + \
				"teams to equal the highest score of the season with a haul of " + str(fixture_score) + "pts"
			
			#If only one team equalled a previously set season high score
			elif season_max_score_count > 1:
				msg = "Equalled the largest score of the season with a haul " + str(fixture_score) + "pts"
			
			#if a new season high-score was set by ONE team this gw...
			else:
				msg = "Set an new largest score of the season with a haul " + str(fixture_score) + "pts"
			
			stats.append(msg)

		#Lowest score on the season
		if fixture_score == season_min_score and gw > 1:
			#if multiple teams set a new season high-score		
			if season_min_score_count > 1 and gameweek_min_score_count > 1 and season_min_score_count == gameweek_min_score_count:
				msg = "Was one of " + str(gameweek_min_score_count) + \
				"teams to set a new season-low score in GW" + str(gw) + " with " + str(fixture_score) + "pts"
			
			#if multiple teams equalled a previously set season high-score		
			elif season_min_score_count > 1 and gameweek_min_score_count > 1:
				msg = "Was one of " + str(gameweek_min_score_count) + \
				"teams to equal the lowest score of the season with " + str(fixture_score) + "pts"
			
			#If only one team equalled a previously set season high score
			elif season_min_score_count > 1:
				msg = "Equalled the lowest score of the season with " + str(fixture_score) + "pts"
			
			#if a new season high-score was set by ONE team this gw...
			else:
				msg = "Set an new lowest score of the season with " + str(fixture_score) + "pts"
			
			stats.append(msg)

		#if team scored top score of GW
		if fixture_score == gameweek_max_score:

			#if more than one team topped the scoreboard...
			if gameweek_max_score_count > 1:
				msg = "Were one of " + str(written_number(gameweek_max_score_count)) +\
				" teams to top the GW" + str(gw) + " scoreboard with a haul " + str(fixture_score) + "pts"
			#if only one team topped the scoreboard...
			else:
				msg =  "Topped the GW" + str(gw) + " scoreboard with a haul of " + str(fixture_score) + "pts"


			# How many times has the team had the top score?
			msg += " – the " + str(ord(fix[team]["fixture_score_rank_array"].count(1))) +\
				" time this season"

			#Have they topped the scores for multiple consecutive weeks?
			multiple_weeks = 0
			for idx, v in enumerate(reversed(fix[team]["fixture_score_rank_array"])):
				if v == 1:
					multiple_weeks += 1
				else:
					break

			if multiple_weeks > 1:
				msg += " and " + str(ord(multiple_weeks) + " week in a row")
			
			msg += " they have had the highest score"

			stats.append(msg)


		#if team scored lowest score of GW
		elif fixture_score == gameweek_min_score:

			#if more than one team...
			if gameweek_min_score_count > 1:
				msg = "Were one of " + str(written_number(gameweek_min_score_count)) +\
				" teams to score " + str(fixture_score) + "pts – the lowest score of Round " + str(gw)
			#if only one team topped the scoreboard...
			else:
				msg =  "Had the lowest score of Round " + str(gw)

			stats.append(msg)

		#if a team set a personal best or worst score
		personal_best_score = max(fix[team]["fixture_score_array"])
		personal_best_score_count = list(fix[team]["fixture_score_array"]).count(personal_best_score)
		personal_worst_score = min(fix[team]["fixture_score_array"])
		personal_worst_score_count = list(fix[team]["fixture_score_array"]).count(personal_worst_score)

		if fixture_score == personal_best_score and gw > 1:
			if personal_best_score_count > 1:
				msg = "Equalled their highest score of the campaign"
			else:
				msg = "Scored their highest single score of the campaign"
			stats.append(msg)
		
		elif fixture_score == personal_worst_score and gw > 1:
			if personal_worst_score_count > 1:
				msg = "Equalled their lowest score of the campaign"
			else:
				msg = "Scored their lowest single score of the campaign"
			stats.append(msg)
		
		#100+ scores
		if fixture_score > 99:
			treble_count = len([i for i in fix[team]["fixture_score_array"] if i > 99])
			msg = "Posted their " + str(ord(treble_count)) + " treble-figure haul of the season."
			stats.append(msg)
		

		fixture_margin = fix[team]["fixture_margin"]

		if fixture_margin == gameweek_max_margin:
			if gameweek_max_margin_count > 1:
				msg = "Were one of " + str(written_number(gameweek_max_margin_count)) +\
				" teams to beat their opponent by " + str(fixture_margin) + "pts – the biggest winning margin of Round " + str(gw)
			else:
				msg = "Enjoyed the largest winning margin of Round " + str(gw) + ", beating their oppenent by " + str(fixture_margin) + "pts"
			stats.append(msg)

		#personal biggest win or defeat
		personal_biggest_win_margin = max(fix[team]["fixture_margin_array"])
		personal_biggest_win_margin_count = list(fix[team]["fixture_margin_array"]).count(personal_biggest_win_margin)
		personal_biggest_loss_margin = min(fix[team]["fixture_margin_array"])
		personal_biggest_loss_margin_count = list(fix[team]["fixture_margin_array"]).count(personal_biggest_loss_margin)

		if fixture_margin > 0 and fixture_margin == personal_biggest_win_margin and gw > 1:
			if personal_biggest_win_margin_count > 1:
				msg = "Equalled their largest win of the season with a " +\
				str(fixture_margin) + "pt margin of victory"
			else:
				msg = "Enjoyed their largest win of the season with a " +\
				str(fixture_margin) + "pt margin of victory"
			stats.append(msg)


		elif fixture_margin < 0 and fixture_margin == personal_biggest_loss_margin and gw > 1:
			if personal_biggest_loss_margin_count > 1:
				msg = "Equalled their heaviest defeat of the season, losing by a " +\
				str(-fixture_margin) + "pt margin"

			else:
				msg = "Suffered their heaviest defeat of the season, losing by a " +\
				str(-fixture_margin) + "pt margin"
			stats.append(msg)


		#result
		fixture_result = fix[team]["fixture_result_array"][-1]
		result_count = list(fix[team]["fixture_result_array"]).count(fixture_result)
		msg = "Recorded their " + str(ord(result_count)) + " " + fixture_result + " of the campaign"
		stats.append(msg)

		identical_result_streak = 0

		#calculate how many identical results have occurred in a row
		for idx, x in enumerate(reversed(fix[team]["fixture_result_array"])):
			if x != fixture_result:
				identical_result_streak = int(idx+1)
				break

		#if it's a streak
		if identical_result_streak > 1:
			if fixture_result == "win":
				msg = "Bagged "
			elif fixture_result == "loss":
				msg = "Endured "
			elif fixture_result == "draw":
				msg = "Chalked up "

			msg += "a " + str(ord(identical_result_streak)) + " " + fixture_result + " in a row"

			stats.append(msg)


			



		if len(stats) > 0:
			msg = str(fix[team]["team_name"]) + ":\n"
			for i in stats:
				msg += "– " + str(i) + "\n"
			return msg
		


	#for each fixture...
	for fix in sorted_fx_list:

		# print(f"fix_combined_score: {fix['fix_combined_score']}")
		# print(f"{[x['fix_combined_score'] for x in sorted_fx_list]}")
		# print(f"Max: {max([x['fix_combined_score'] for x in sorted_fx_list])}")
		# print(f"Min: {min([x['fix_combined_score'] for x in sorted_fx_list])}")

		#fixture and scoreline
		fixture_scoreline = str(fix["home_team"]["team_name"]) + " " + str(fix["home_team"]["fixture_score"]) +\
		" – " + str(fix["away_team"]["fixture_score"]) + " " + str(fix["away_team"]["team_name"])
		print_statements.append(fixture_scoreline)


		#calculate season and gameweek-sepcific mins, maxs, etc...
		season_scores = list(item for sublist in d_fxdata["fixture_scores"][:int(gw)] for item in sublist)
		season_max_score = max(season_scores)
		season_max_score_count = season_scores.count(season_max_score)
		season_min_score = min(season_scores)
		season_min_score_count = season_scores.count(season_min_score)

		season_margins = list([item for sublist in d_fxdata["fixture_margins"][:int(gw)] for item in sublist])
		season_max_margin = max(season_margins)
		season_max_margin_count = season_margins.count(season_max_margin)

		gameweek_scores = list(d_fxdata["fixture_scores"][gw-1])
		gameweek_max_score = max(gameweek_scores)
		gameweek_max_score_count = gameweek_scores.count(gameweek_max_score)
		gameweek_min_score = min(gameweek_scores)
		gameweek_min_score_count = gameweek_scores.count(gameweek_min_score)

		gameweek_margins = list(d_fxdata["fixture_margins"][gw-1])
		gameweek_max_margin = max(gameweek_margins)
		gameweek_max_margin_count = gameweek_margins.count(gameweek_max_margin)

		gameweek_combined_scores = [x["fix_combined_score"] for x in sorted_fx_list]
		gameweek_max_combined_score = max(gameweek_combined_scores)
		gameweek_max_combined_score_count = gameweek_combined_scores.count(gameweek_max_combined_score)
		gameweek_min_combined_score = min(gameweek_combined_scores)
		gameweek_min_combined_score_count = gameweek_combined_scores.count(gameweek_min_combined_score)

		
		#highest-scoring fixture of the gameweek?
		if fix["fix_combined_score"] == gameweek_max_combined_score:
			#if multiple teams set a new season high-score		
			if gameweek_max_combined_score_count > 1:
				msg = "One of " + str(gameweek_max_combined_score_count) + \
				"highest-scoring fixtures in GW" + str(gw)
			else:
				msg = "The highest-scoring fixture of GW" + str(gw)

			msg += " with a combined score of " + str(fix["fix_combined_score"]) + "pts"
			print_statements.append(msg)

		#lowest-scoring fixture of the gameweek?
		if fix["fix_combined_score"] == gameweek_min_combined_score:
			#if multiple teams set a new season high-score		
			if gameweek_min_combined_score_count > 1:
				msg = "One of " + str(gameweek_min_combined_score_count) + \
				"lowest-scoring fixtures in GW" + str(gw)
			else:
				msg = "The lowest-scoring fixture of GW" + str(gw)

			msg += " with a combined score of " + str(fix["fix_combined_score"]) + "pts"
			print_statements.append(msg)



		print_statements.append(str(stats("home_team")))
		print_statements.append(str(stats("away_team")))


	for x in print_statements:
		print(x)


for w in range(1,len(d_fixtures)+1):

	gw_stats(w)
	fx_stats(w)
	print("")


