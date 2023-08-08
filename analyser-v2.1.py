import json
from collections import Counter

# load database
season_dir = './seasons/2023'	#edit this to target different seasons

database_path = season_dir + '/builders/~ templates/database.json'
fixtures_path = season_dir + '/data/fixture-list.json'

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

	#fixture_scores
	if "fixture_scores" not in d_gwdata:
		d_gwdata["fixture_scores"] = val['fixture_score_array'].copy()
	else:
		#if the list already exists, add together the scores
		for idx, v in enumerate(val['fixture_score_array']):
			d_gwdata["fixture_scores"][idx]+=v

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
	if len(d_gwdata["fixture_scores"]) < gw:
		print("Gameweek "+ str(gw) +" has not yet been played")
		return


	#create an empty list to store statements in
	print_statements = []

	###############
	#scores
	scores = d_gwdata["fixture_scores"][:(gw)]
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
			str(comma_format(d_gwdata["fixture_scores"][int(gw-1)]))
	
	#lowest score after GW4
	elif score_rank == gw and gw > 4:
		message = "Round " + str(gw) + " was the lowest-scoring week of the season so far,"\
			" with a combined total of just " +\
			str(comma_format(d_gwdata["fixture_scores"][int(gw-1)]))

	#top-five score after GW9
	elif score_rank <= 5 and gw > 9:
		message = "Round " + str(gw) + " was the " + ord(score_rank) +\
		"-highest-scoring week of the season so far, with a combined total of " +\
			str(comma_format(d_gwdata["fixture_scores"][int(gw-1)]))

	#bottom-five score after GW9
	elif score_rank >= (gw-4) and gw > 9:
		message = "Round " + str(gw) + " was the " + ord(gw-score_rank+1) +\
		"-lowest-scoring week of the season so far, with a combined total of only " +\
			str(comma_format(d_gwdata["fixture_scores"][int(gw-1)]))

	#any other score
	else:
		message = "Round " + str(gw) + " saw Chumpionship teams score a combined total of " +\
			str(comma_format(d_gwdata["fixture_scores"][int(gw-1)])) +\
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
– Top scoring team that GW? *
– Lowest scoring team that GW? *

– Personal best scores? *
– Personal lowest scores? *

- Highest single score of the season?
- Lowest single score of the season?

- How many teams set pb/pw scores that gw?

– Biggest winning margin that GW?
– Personal biggest win / loss?*

– League pos delta
–– Beaten a team +10 or more places higher in table?

– Chip value
– Most transfers made tht GW

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

	#for each fixture in defined gameweek...
	for fix in d_fixtures[str("GW"+format_two_digit(gw))]:
		fx_dict = {}

		for key, val in fix.items():
			
			fx_dict[str(key)] = {
				"fpl_code": val,
				"team_name": str(d_data[str(val)]["team_name"]),
				"manager_name": str(d_data[str(val)]["manager_name"]),
				"manager_firstname": str(d_data[str(val)]["manager_name"]).split()[0],
				"manager_surname": str(d_data[str(val)]["manager_name"]).split()[1],

				#array of all scores to date, to assess highest/lowest since...
				"fixture_score_array": d_data[str(val)]["fixture_score_array"][:int(gw)],
				"fixture_score": d_data[str(val)]["fixture_score_array"][int(gw-1)],

				#array of all score ranks to date, to assess highest/lowest since...
				"fixture_score_rank_array": d_data[str(val)]["fixture_score_rank_array"][:int(gw)],
				"fixture_score_rank": d_data[str(val)]["fixture_score_rank_array"][int(gw-1)],

				#array of all score margins to date, to assess highest/lowest since...
				"fixture_margin_array": d_data[str(val)]["fixture_margin_array"][:int(gw)],
				"fixture_margin": d_data[str(val)]["fixture_margin_array"][int(gw-1)],


			}

		fx_list.append(fx_dict)

	# sort the list by home team name
	sorted_fx_list = sorted(fx_list, key=lambda x: x["home_team"]["team_name"])

	#devise a better, score-based ordering system later

	print_statements = []

	def stats(team):
		msg = ""

		fixture_score = fix[team]["fixture_score"]

		#if team scored top score
		if fixture_score == gameweek_max_score:
			msg += str(fix[team]["team_name"])
			
			#if more than one team topped the scoreboard...
			if gameweek_max_score_count > 1:
				msg += " were one of " + str(written_number(gameweek_max_score_count)) +\
				" teams to top the GW" + str(gw) + " scoreboard "
			#if only one team topped the scoreboard...
			else:
				msg +=  " topped the GW" + str(gw) + " scoreboard "

			#msg += " with a haul of " + str(fixture_score) + "pts"

			add = []

			# How many times has the team had the top score?
			if fix[team]["fixture_score_rank_array"].count(1) == 1 and gw > 5 or\
			fix[team]["fixture_score_rank_array"].count(1) > 1:
				add.append("– the " + str(ord(fix[team]["fixture_score_rank_array"].count(1))) +\
				" time this season ")

			#Have they topped the scores for multiple consecutive weeks?
			multiple_weeks = 0
			for idx, v in enumerate(reversed(fix[team]["fixture_score_rank_array"])):
				if v == 1:
					multiple_weeks += 1
				else:
					break

			if multiple_weeks > 1:

				if len(add) > 0:
					add.append("and ")
				else: 
					add.append("– the ")

				add.append(str(ord(multiple_weeks)) + " week on the bounce ")
			
			if len(add) > 0:
				add.append(str(fix[team]["manager_surname"]) + " has had the highest score ")

			for x in add:
				msg += x


		#if team scored lowest score
		if fixture_score == gameweek_min_score:
			msg += str(fix[team]["team_name"])

			#if more than one team...
			if gameweek_min_score_count > 1:
				msg += " were one of " + str(written_number(gameweek_min_score_count)) +\
				" teams with the lowest score of Round " + str(gw) + " "
			#if only one team topped the scoreboard...
			else:
				msg +=  " scored the fewest points in Round " + str(gw) + " "


		#if a team set a personal best score
		personal_best_score = max(fix[team]["fixture_score_array"])
		#personal_best_score_count = list(fix[team]["fixture_score_array"]).count(personal_best_score)
		personal_best_score_count = len([i for i in fix[team]["fixture_score_array"] if i == personal_best_score])

		if fixture_score == personal_best_score and gw > 5:

			if len(msg) == 0:
				if personal_best_score_count > 1:
					msg += str(fix[team]["team_name"]) + " equalled their highest score of the campaign. "
				else:
					msg += str(fix[team]["team_name"]) + " posted their highest score of the campaign. "

			else:
				if personal_best_score_count > 1:
					msg += "– and equalled their highest score of the campaign. "
				else:
					msg += "– with their highest score of the campaign. "

		#if a team set a personal worst score
		personal_worst_score = min(fix[team]["fixture_score_array"])
		personal_worst_score_count = list(fix[team]["fixture_score_array"]).count(personal_worst_score)
		
		if fixture_score == personal_worst_score and gw > 5:
			if len(msg) == 0:
				if personal_worst_score_count > 1:
					msg += str(fix[team]["team_name"]) + " equalled their lowest score of the campaign. "
				else:
					msg += str(fix[team]["team_name"]) + " slumped to their lowest score of the campaign. "

			else:
				if personal_worst_score_count > 1:
					msg += "– and equalled their lowest score of the campaign. "
				else:
					msg += "– with their lowest score of the campaign. "

		#100+ scores
		if fixture_score > 99:
			treble_count = len([i for i in fix[team]["fixture_score_array"] if i > 99])
			msg += str(fix[team]["team_name"]) + " posted their " + str(ord(treble_count)) + " treble-figure haul of the season. "
		

		fixture_margin = fix[team]["fixture_margin"]

		#biggest win of the week
		if fixture_margin == gameweek_max_margin:

		#personal biggest win
		personal_biggest_win_margin = max(fix[team]["fixture_margin_array"])
		personal_biggest_win_margin_count = list(fix[team]["fixture_margin_array"]).count(personal_biggest_win_margin)

		if fixture_margin > 0 and fixture_margin == personal_biggest_win_margin:
			msg += str(fix[team]["team_name"])

			if personal_biggest_win_margin_count > 1:
				msg += " equalled their largest win of the season so far with a " +\
				str(fixture_margin) + "pt margin of victory. "

			else:
				msg += " enjoyed their largest win of the season so far with a " +\
				str(fixture_margin) + "pt margin of victory. "

		#personal biggest defeat
		personal_biggest_loss_margin = min(fix[team]["fixture_margin_array"])
		personal_biggest_loss_margin_count = list(fix[team]["fixture_margin_array"]).count(personal_biggest_loss_margin)

		if fixture_margin < 0 and fixture_margin == personal_biggest_loss_margin:
			msg += str(fix[team]["team_name"])

			if personal_biggest_loss_margin_count > 1:
				msg += " equalled their heaviest defeat of the season so far, losing by a " +\
				str(fixture_margin) + "pt margin. "

			else:
				msg += " endured their heaviest defeat of the season so far, losing by a " +\
				str(fixture_margin) + "pt margin. "



		return msg


	#for each fixture...
	for fix in sorted_fx_list:

		#fixture and scoreline
		message = str(fix["home_team"]["team_name"]) + " " + str(fix["home_team"]["fixture_score"]) +\
		" – " + str(fix["away_team"]["fixture_score"]) + " " + str(fix["away_team"]["team_name"])

		#add message to statements list
		if len(message) > 0:
			print_statements.append(message)
			message = ""	#reset

		#calculate gameweek-sepcific mins, maxs, etc...
		gameweek_scores = list(d_fxdata["fixture_scores"][gw-1])
		gameweek_max_score = max(gameweek_scores)
		gameweek_max_score_count = gameweek_scores.count(gameweek_max_score)
		gameweek_min_score = min(gameweek_scores)
		gameweek_min_score_count = gameweek_scores.count(gameweek_min_score)

		gameweek_margins = list(d_fxdata["fixture_margins"][gw-1])
		gameweek_max_margin = max(gameweek_margins)
		gameweek_max_margin_count = gameweek_margins.count(gameweek_max_margin)

		#exceptional landmarks that require an alt approach... 

		#Both top-scoring teams 
		if fix["home_team"]["fixture_score"] == gameweek_max_score and fix["away_team"]["fixture_score"] == gameweek_max_score:
			message += str(fix["home_team"]["team_name"]) + " and " + str(fix["away_team"]["team_name"]) +\
			" hauled in " + str(gameweek_max_score) + " apiece to top the GW" + str(gw) + " scoreboard"
			print_statements.append(message)

		else:
			message += str(stats("home_team"))

			#add message to statements list
			if len(message) > 0 :
				print_statements.append(message)
				message = ""	#reset

			message += str(stats("away_team"))

			#add message to statements list
			if len(message) > 0 :
				print_statements.append(message)
				message = ""	#reset


	for x in print_statements:
		print(x)


for w in range(1,len(d_fixtures)+1):

	gw_stats(w)
	fx_stats(w)
	print("")


