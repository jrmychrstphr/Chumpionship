import json

# load database
database_dir = './seasons/2023/builders/~ templates'
database_path = database_dir + '/database.json'

with open(database_path) as f:
	data = json.load(f)


# define gameweek
gameweeks = [1,1]


d_list = []
team_dict = {}


#lists to store results to print later
p_list_szn_stats = []
p_list_gameweek_stats = []


for key, val in data.items():

	d_obj = {

		#player info
		'manager_code': val['fpl_code'],
		'manager_name': val['manager_name'],
		'team_name': val['team_name'],
		'opponents': val['fixture_opponent_array'],

		# data for season-to-date (ie, to latest gw in range)
		'szn_total_score': sum(val['fixture_score_array'][:gameweeks[1]]),
		'szn_fixture_scores': val['fixture_score_array'][:gameweeks[1]],
		'szn_highest_fixture_score': max(val['fixture_score_array'][:gameweeks[1]]),
		'szn_lowest_fixture_score': min(val['fixture_score_array'][:gameweeks[1]]),
		'szn_fixture_margins': val['fixture_margin_array'][:gameweeks[1]],
		'szn_highest_fixture_margin': max(val['fixture_margin_array'][:gameweeks[1]]),
		'szn_lowest_fixture_margin': min(val['fixture_margin_array'][:gameweeks[1]]),
		'szn_league_position': val['league_position_array'][:gameweeks[1]],

		# data sliced by range
		'range_total_score': sum(val['fixture_score_array'][gameweeks[0]-1:gameweeks[1]]),
		'range_fixture_scores': val['fixture_score_array'][gameweeks[0]-1:gameweeks[1]],
		'range_highest_fixture_score': max(val['fixture_score_array'][gameweeks[0]-1:gameweeks[1]]),
		'range_lowest_fixture_score': min(val['fixture_score_array'][gameweeks[0]-1:gameweeks[1]]),
		'range_fixture_margins': val['fixture_margin_array'][gameweeks[0]-1:gameweeks[1]],
		'range_highest_fixture_margin': max(val['fixture_margin_array'][gameweeks[0]-1:gameweeks[1]]),
		'range_lowest_fixture_margin': min(val['fixture_margin_array'][gameweeks[0]-1:gameweeks[1]]),
		'range_league_position': val['league_position_array'][gameweeks[0]-1:gameweeks[1]]
	}

	team_dict[d_obj['manager_code']] = {
		'manager_name': val['manager_name'],
		'team_name': val['team_name'],		
	}

	d_list.append(d_obj)


d = d_list.copy()


## Highest overall score, szn to date
m = max(d, key=lambda d: d['szn_total_score'])["szn_total_score"]

p_list_szn_stats.append("")
p_list_szn_stats.append(f"Highest overall score: {'{:,}'.format(m)}pts")

for x in d:
	if x['szn_total_score'] == m:
		p_list_szn_stats.append(f"{x['manager_name']} ({x['team_name']})")


## Highest overall score, end of range
m = max(d, key=lambda d: d['range_total_score'])["range_total_score"]

p_list_gameweek_stats.append("")
p_list_gameweek_stats.append(f"Most points scored during this period: {'{:,}'.format(m)}pts")

for x in d:
	if x['range_total_score'] == m:
		p_list_gameweek_stats.append(f"{x['manager_name']} ({x['team_name']})")


## Lowest overall score, szn to date
m = min(d, key=lambda d: d['szn_total_score'])["szn_total_score"]

p_list_szn_stats.append("")
p_list_szn_stats.append(f"Lowest overall score: {'{:,}'.format(m)}pts")

for x in d:
	if x['szn_total_score'] == m:
		p_list_szn_stats.append(f"{x['manager_name']} ({x['team_name']})")


## Lowest overall score, end of range
m = min(d, key=lambda d: d['range_total_score'])["range_total_score"]

p_list_gameweek_stats.append("")
p_list_gameweek_stats.append(f"Fewest points scored during this period: {'{:,}'.format(m)}pts")

for x in d:
	if x['range_total_score'] == m:
		p_list_gameweek_stats.append(f"{x['manager_name']} ({x['team_name']})")


## Highest fixture score, szn to date
m = max(d, key=lambda d: d['szn_highest_fixture_score'])["szn_highest_fixture_score"]

p_list_szn_stats.append("")
p_list_szn_stats.append(f"Highest fixture score: {'{:,}'.format(m)}pts")

for x in d:
	for idx, val in enumerate(x['szn_fixture_scores']):
		if val == m:
			p_list_szn_stats.append(f"{x['manager_name']} ({x['team_name']}), GW{idx+1} vs {team_dict[x['opponents'][idx]]['team_name']}")

## Lowest fixture score, szn to date
m = min(d, key=lambda x:x["szn_lowest_fixture_score"])["szn_lowest_fixture_score"]

p_list_szn_stats.append("")
p_list_szn_stats.append(f"Lowest fixture score: {'{:,}'.format(m)}pts")

for x in d:
	for idx, val in enumerate(x['szn_fixture_scores']):
		if val == m:
			p_list_szn_stats.append(f"{x['manager_name']} ({x['team_name']}), GW{idx+1} vs {team_dict[x['opponents'][idx]]['team_name']}")


# Highest fixture score during period
m = max(d, key=lambda d: d['range_highest_fixture_score'])["range_highest_fixture_score"]

p_list_gameweek_stats.append("")
p_list_gameweek_stats.append(f"Highest single fixture score set during period: {'{:,}'.format(m)}pts")

for x in d:
	if m in x["range_fixture_scores"]:
		for idx, val in enumerate(x["range_fixture_scores"]):
			if val == m:
				p_list_gameweek_stats.append(f"{x['manager_name']} ({x['team_name']}), GW{gameweeks[0]+idx} vs {team_dict[x['opponents'][gameweeks[0]+(idx-1)]]['team_name']}")


# Lowest fixture score during period
m = min(d, key=lambda x:x["range_lowest_fixture_score"])["range_lowest_fixture_score"]

p_list_gameweek_stats.append("")
p_list_gameweek_stats.append(f"Lowest single fixture score set during period: {'{:,}'.format(m)}pts")

for x in d:
	if m in x["range_fixture_scores"]:
		for idx, val in enumerate(x["range_fixture_scores"]):
			if val == m:
				p_list_gameweek_stats.append(f"{x['manager_name']} ({x['team_name']}), GW{gameweeks[0]+idx} vs {team_dict[x['opponents'][gameweeks[0]+(idx-1)]]['team_name']}")



##	Biggest margin of victory, szn to date
m = max(d, key=lambda x:x["szn_highest_fixture_margin"])["szn_highest_fixture_margin"]

p_list_szn_stats.append("")
p_list_szn_stats.append(f"Largest winning margin: {'{:,}'.format(m)}pts")

for x in d:
	for idx, val in enumerate(x['szn_fixture_margins']):
		if val == m:
			p_list_szn_stats.append(f"{x['manager_name']} ({x['team_name']}), GW{idx+1} vs {team_dict[x['opponents'][idx]]['team_name']}")


##	Biggest margin of victory during period
m = max(d, key=lambda x:x["range_highest_fixture_margin"])["range_highest_fixture_margin"]

p_list_gameweek_stats.append("")
p_list_gameweek_stats.append(f"Largest winning margin during period: {'{:,}'.format(m)}pts")

for x in d:
	for idx, val in enumerate(x['range_fixture_margins']):
		if val == m:
			p_list_gameweek_stats.append(f"{x['manager_name']} ({x['team_name']}), GW{gameweeks[0]+idx} vs {team_dict[x['opponents'][gameweeks[0]+(idx-1)]]['team_name']}")



#################
##	Result streaks

streaks = []

for x in d:

	# chunk fixture margins list by streaks
	s = []

	for idx, val in enumerate(x['szn_fixture_margins']):

		o = { "gw": idx+1,"margin": val	}

		if idx == 0:
			s.append([o])
		else:
			p = x['szn_fixture_margins'][idx-1]

			if p > 0 and val > 0 or p <= 0 and val <= 0 :
				s[len(s)-1].append(o)
			else:
				s.append([o])

	#split streaks in to two lists:
	win_streak_list, winless_streak_list = [],[]

	for idx, val in enumerate(s):
		if sum(item["margin"] for item in val) > 0:
			win_streak_list.append(val)
		else:
			winless_streak_list.append(val)

	temp_ob = {
		"manager_name": x["manager_name"],
		"team_name": x["team_name"],
		"streaks": s,
		"longest_win_streak": {
			"length": 0,
			"instances": []
		},
		"longest_winless_streak": {
			"length": 0,
			"instances": []
		},
		"current_streak_length": 0
	}

	if len(win_streak_list) > 0: temp_ob["longest_win_streak"]["length"] = len(max(win_streak_list, key=len))
	if len(winless_streak_list) > 0: temp_ob["longest_winless_streak"]["length"] = len(max(winless_streak_list, key=len))

	for item in win_streak_list :
		if len(item) == len(max(win_streak_list, key=len)):
			t = {"start": item[0]['gw'], "end": item[len(item)-1]['gw']}
			temp_ob["longest_win_streak"]["instances"].append(t)

	for item in winless_streak_list :
		if len(item) == len(max(winless_streak_list, key=len)):
			t = {"start": item[0]['gw'], "end": item[len(item)-1]['gw']}
			temp_ob["longest_winless_streak"]["instances"].append(t)

	#if len(s[-1]) > 0: temp_ob["current_streak"]["length"] = len(s[-1])

	streaks.append(temp_ob)


#szn longest win streaks
m = max(streaks, key=lambda x:x['longest_win_streak']['length'])['longest_win_streak']['length']

p_list_szn_stats.append("")
p_list_szn_stats.append(f"Longest winning streak: {'{:,}'.format(m)} weeks")

for x in streaks :
	if x['longest_win_streak']['length'] == m:
		for idx, val in enumerate(x['longest_win_streak']['instances']):
			p_list_szn_stats.append(f"{x['manager_name']} ({x['team_name']}), GWs {val['start']}–{val['end']}")


#szn longest winless streaks
m = max(streaks, key=lambda x:x['longest_winless_streak']['length'])['longest_winless_streak']['length']

p_list_szn_stats.append("")
p_list_szn_stats.append(f"Longest streak without a win: {'{:,}'.format(m)} weeks")

for x in streaks :
	if x['longest_winless_streak']['length'] == m:
		for idx, val in enumerate(x['longest_winless_streak']['instances']):
			p_list_szn_stats.append(f"{x['manager_name']} ({x['team_name']}), GWs {val['start']}–{val['end']}")

# Longest current win streak
f = [x for x in streaks if sum(item['margin'] for item in x['streaks'][-1]) > 0]
m = len(max(f, key=lambda x:len(x['streaks'][-1]))['streaks'][-1])

p_list_gameweek_stats.append("")
p_list_gameweek_stats.append(f"Longest streak of wins at the end of period: {'{:,}'.format(m)} weeks")

for x in streaks :
	if sum(item['margin'] for item in x['streaks'][-1]) > 0 and m == len(x['streaks'][-1]):
		p_list_gameweek_stats.append(f"{x['manager_name']} ({x['team_name']}), GWs {x['streaks'][-1][0]['gw']}–{x['streaks'][-1][-1]['gw']}")


# Longest current win streak
f = [x for x in streaks if sum(item['margin'] for item in x['streaks'][-1]) <= 0]
m = len(max(f, key=lambda x:len(x['streaks'][-1]))['streaks'][-1])

p_list_gameweek_stats.append("")
p_list_gameweek_stats.append(f"Longest winless streak at the end of period: {'{:,}'.format(m)} weeks")

for x in streaks :
	if sum(item['margin'] for item in x['streaks'][-1]) <= 0 and m == len(x['streaks'][-1]):
		p_list_gameweek_stats.append(f"{x['manager_name']} ({x['team_name']}), GWs {x['streaks'][-1][0]['gw']}–{x['streaks'][-1][-1]['gw']}")





p_divider = "–––––––––––––––––––––––––––"

# Print results to console
print(p_divider)
print(f"Season to date (GW{gameweeks[1]})")
print(p_divider)
for x in p_list_szn_stats:
	print(x)


for i in range(5):
	print("")

# Gameweek(s) stats
print(p_divider)
print(f"GWs {gameweeks[0]}–{gameweeks[1]} only")
print(p_divider)
for x in p_list_gameweek_stats:
	print(x)


#	Season stats
##	Highest overall score *
##	Lowest overall score *
##	Highest fixture score *
##	Lowest fixture score *
##	Biggest margin of victory *
##	Longest win streak *
##	Longest winless streak *

#	Stats during defined period
##	Highest overall score during period *
##	Lowest overall score  during period *
##	Highest fixture score in range *
##	Lowest fixture score in range * 
##	Biggest margin of victory in range *
##	Longest result streak at end of range, wins and winless *
##	Best form across period (ie, most league points won)
##	Biggest league positional changes, up and down

#	Team landmarks
##	Has team set a highest score / PB?
##	Has team set a largest win or loss?
##	Has team topped the league? First time? Nth team to top the league...
##	Has team entered the top-four? First time? Number of consecutive weeks in top-four?
##	Has team entered the bottom-three? First time?  Number of consecutive weeks in bottom-three?