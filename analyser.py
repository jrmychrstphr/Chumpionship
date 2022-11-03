import json
from collections import Counter

# load database
database_dir = './seasons/2023/builders/~ templates'
database_path = database_dir + '/database.json'

with open(database_path) as f:
	data = json.load(f)

# useful functions
def ord(n):
    return str(n)+("th" if 4<=n%100<=20 else {1:"st",2:"nd",3:"rd"}.get(n%10, "th"))

# define gameweeks
def return_gameweeks(n):
	n = str(n)
	l = n.split("-")

	if len(l) < 3: g = list(range(int(l[0]),int(l[-1])+1))
	else: g = False

	print(f"gameweeks = {g}")
	return g

gameweeks = return_gameweeks("14")

# compile dataset

dataset = []
teams = {}

for key, val in data.items():

	teams[val['fpl_code']] = {
		'manager_name': val['manager_name'],
		'team_name': val['team_name'],		
	}

	d_obj = {

		#player info
		'manager_code': val['fpl_code'],
		'manager_name': val['manager_name'],
		'team_name': val['team_name'],
		'opponents': val['fixture_opponent_array'],


		# data across gameweeks range
		'range_fixture_scores': val['fixture_score_array'][gameweeks[0]-1:gameweeks[-1]],
		'range_total_score': sum(val['fixture_score_array'][gameweeks[0]-1:gameweeks[-1]]),
		'range_highest_fixture_score': max(val['fixture_score_array'][gameweeks[0]-1:gameweeks[-1]]),
		'range_lowest_fixture_score': min(val['fixture_score_array'][gameweeks[0]-1:gameweeks[-1]]),
		'range_fixture_margins': val['fixture_margin_array'][gameweeks[0]-1:gameweeks[-1]],
		'range_highest_fixture_margin': max(val['fixture_margin_array'][gameweeks[0]-1:gameweeks[-1]]),
		'range_league_positions': val['league_position_array'][gameweeks[0]-1:gameweeks[-1]],
		'range_chips_played': val['chip_played_array'][gameweeks[0]-1:gameweeks[-1]],
		'range_transfers_made': val['transfers_made_array'][gameweeks[0]-1:gameweeks[-1]],
		'range_total_transfers_made': sum(val['transfers_made_array'][gameweeks[0]-1:gameweeks[-1]]),
		'range_transfered_in': val['transfered_in_array'][gameweeks[0]-1:gameweeks[-1]],
		'range_transfered_out': val['transfered_out_array'][gameweeks[0]-1:gameweeks[-1]],
		'range_captains': val['captains_array'][gameweeks[0]-1:gameweeks[-1]],
		'range_league_positions': val['league_position_array'][gameweeks[0]-1:gameweeks[-1]],


		# data at the end of gameweeks range (ie, season so far)
		'season_fixture_scores': val['fixture_score_array'][:gameweeks[-1]],
		'season_total_score': sum(val['fixture_score_array'][:gameweeks[-1]]),
		'season_highest_fixture_score': max(val['fixture_score_array'][:gameweeks[-1]]),
		'season_lowest_fixture_score': min(val['fixture_score_array'][:gameweeks[-1]]),
		'season_fixture_margins': val['fixture_margin_array'][:gameweeks[-1]],
		'season_highest_fixture_margin': max(val['fixture_margin_array'][:gameweeks[-1]]),
		'season_league_positions': val['league_position_array'][:gameweeks[-1]],
		'season_chips_played': val['chip_played_array'][:gameweeks[-1]],
		'season_league_positions': val['league_position_array'][:gameweeks[-1]],

	}

	dataset.append(d_obj)


### analyse datset ###

d = dataset.copy()
notifications = []

n_divider = "*" * 30

### Range ###
notifications.append(f"{n_divider}")

if len(gameweeks) == 1 :
	notifications.append(f"Stats for GW{gameweeks[0]}")
elif len(gameweeks) != 0 :
	notifications.append(f"Stats across GWs {gameweeks[0]}–{gameweeks[-1]}")

notifications.append(f"{n_divider}")


# Highest overall score
m = max(d, key=lambda d: d['range_total_score'])["range_total_score"]
notifications.append(f"Most points scored: {'{:,}'.format(m)}pts")
for x in d:
	if x['range_total_score'] == m:
		notifications.append(f">> {x['manager_name']} ({x['team_name']})")
notifications.append(f"")


# Lowest overall score
m = min(d, key=lambda d: d['range_total_score'])["range_total_score"]
notifications.append(f"Fewest points scored: {'{:,}'.format(m)}pts")
for x in d:
	if x['range_total_score'] == m:
		notifications.append(f">> {x['manager_name']} ({x['team_name']})")
notifications.append(f"")


# Highest fixture score
m = max(d, key=lambda d: d['range_highest_fixture_score'])["range_highest_fixture_score"]
notifications.append(f"Highest fixture score: {'{:,}'.format(m)}pts")
for x in d:
	for idx, val in enumerate(x['range_fixture_scores']):
		if val == m:
			notifications.append(f">> {x['manager_name']} ({x['team_name']}), {'GW' + str(gameweeks[0]+idx) + ' ' if len(gameweeks) > 1 else ''}vs {teams[x['opponents'][gameweeks[0]+idx-1]]['team_name']}")
notifications.append(f"")


# Lowest fixture score
m = min(d, key=lambda d: d['range_lowest_fixture_score'])["range_lowest_fixture_score"]
notifications.append(f"Lowest fixture score: {'{:,}'.format(m)}pts")
for x in d:
	for idx, val in enumerate(x['range_fixture_scores']):
		if val == m:
			notifications.append(f">> {x['manager_name']} ({x['team_name']}), {'GW' + str(gameweeks[0]+idx) + ' ' if len(gameweeks) > 1 else ''}vs {teams[x['opponents'][gameweeks[0]+idx-1]]['team_name']}")
notifications.append(f"")



# Largest margin of victory
m = max(d, key=lambda x:x["range_highest_fixture_margin"])["range_highest_fixture_margin"]
notifications.append(f"Largest margin of victory: {'{:,}'.format(m)}pts")
for x in d:
	for idx, val in enumerate(x['range_fixture_margins']):
		if val == m:
			notifications.append(f">> {x['manager_name']} ({x['team_name']}), {'GW' + str(gameweeks[0]+idx) if len(gameweeks) > 1 else ''}vs {teams[x['opponents'][gameweeks[0]+idx-1]]['team_name']}")
notifications.append(f"")


# Biggest league position changes
if gameweeks[0] > 1: 
	l = []
	for x in d:
		previous_position = x['season_league_positions'][(gameweeks[0]-2)]
		current_position = x['range_league_positions'][-1]
		league_position_change = current_position - previous_position
		o = {
			'league_position_change': -league_position_change,
			'manager_name': x['manager_name'],
			'team_name': x['team_name'],
			'current_position': current_position,
			'previous_position': previous_position
		}
		l.append(o)

	# biggest upward change
	m = max(l, key=lambda x:x["league_position_change"])["league_position_change"]
	notifications.append(f"Biggest upward change in league position: {m}")
	for x in l: 
		if x['league_position_change'] == m:
			notifications.append(f">> {x['manager_name']} ({x['team_name']}), from {ord(x['previous_position'])} to {ord(x['current_position'])}")
	notifications.append(f"")

	# biggest downward change
	m = min(l, key=lambda x:x["league_position_change"])["league_position_change"]
	notifications.append(f"Biggest downward change in league position: {m}")
	for x in l: 
		if x['league_position_change'] == m:
			notifications.append(f">> {x['manager_name']} ({x['team_name']}), from {ord(x['previous_position'])} to {ord(x['current_position'])}")
	notifications.append(f"")





# Transfers made, total
s = sum(x["range_total_transfers_made"] for x in d)
notifications.append(f"Total transfers made: {s}")
notifications.append(f"")


# Transfers made, most
m = max(d, key=lambda x:x["range_total_transfers_made"])["range_total_transfers_made"]
notifications.append(f"Most transfers made: {m}")
for x in d:
	if x['range_total_transfers_made'] == m:
		notifications.append(f">> {x['manager_name']} ({x['team_name']})")
notifications.append(f"")


# Most transferred-in player
l = []
for x in d:
	for val in x["range_transfered_in"]:
		if val != "":
			l.append(val)
l = [item for sublist in l for item in sublist]

notifications.append(f"Most transferred-in")
if len(l) != 0:
	for x in Counter(l).most_common():
		if x[1] == max(Counter(l).values()):
			notifications.append(f">> {x[0]} ({x[1]})")
			for y in d:
				if str(x[0]) in (item for sublist in y["range_transfered_in"] for item in sublist):
					notifications.append(f"   – {y['manager_name']} ({y['team_name']})")
else: notifications.append(f"No transfers made")
notifications.append(f"")


# Most transferred-out player
l = []
for x in d:
	for val in x["range_transfered_out"]:
		if val != "":
			l.append(val)
l = [item for sublist in l for item in sublist]

notifications.append(f"Most transferred-out")
if len(l) != 0:
	for x in Counter(l).most_common():
		if x[1] == max(Counter(l).values()):
			notifications.append(f">> {x[0]} ({x[1]})")
			for y in d:
				if str(x[0]) in (item for sublist in y["range_transfered_out"] for item in sublist):
					notifications.append(f"   – {y['manager_name']} ({y['team_name']})")
else: notifications.append(f"No transfers made")
notifications.append(f"")


# Most popular captain
l = []
for x in d:
	for val in x["range_captains"]:
		if val != "":
			l.append(val)

notifications.append(f"Most captained")
if len(l) != 0:
	for x in Counter(l).most_common():
		if x[1] == max(Counter(l).values()):
			notifications.append(f">> {x[0]}: {x[1]}")
			for y in d:
				if str(x[0]) in (y["range_captains"]):
					for idx, val in enumerate(y["range_captains"]):
						notifications.append(f"   – {y['manager_name']} ({y['team_name']}){', GW' + str(gameweeks[0]+idx) if len(gameweeks) > 1 else ''}")
notifications.append(f"")



# Chips used
l = []
for x in d:
	for idx, val in enumerate(x['range_chips_played']):
		if val.lower() != "none":
			l.append(f">> {val}: {x['manager_name']} ({x['team_name']}), GW{gameweeks[0]+idx} vs {teams[x['opponents'][gameweeks[0]+idx-1]]['team_name']}")
notifications.append(f"Chips played: {len(l)}")
if len(l) != 0:
	for x in sorted(l):
		notifications.append(f"{x}")
notifications.append(f"")


# Personal best scores set
if gameweeks[0] > 4: 
	l = []
	for x in d:
		for idx, val in enumerate(x['range_fixture_scores']):
			if val == x['season_highest_fixture_score']:
				l.append(f">> {'{:,}'.format(val)}pts {x['manager_name']} ({x['team_name']}), GW{gameweeks[0]+idx} vs {teams[x['opponents'][gameweeks[0]+idx-1]]['team_name']}")
	notifications.append(f"Personal best scores set: {len(l)}")
	if len(l) != 0:
		for x in sorted(l, reverse=True):
			notifications.append(f"{x}")
	notifications.append(f"")


# Personal worst scores set
if gameweeks[0] > 4: 
	l = []
	for x in d:
		for idx, val in enumerate(x['range_fixture_scores']):
			if val == x['season_lowest_fixture_score']:
				l.append(f">> {'{:,}'.format(val)}pts {x['manager_name']} ({x['team_name']}), GW{gameweeks[0]+idx} vs {teams[x['opponents'][gameweeks[0]+idx-1]]['team_name']}")
	notifications.append(f"Personal worst scores set: {len(l)}")
	if len(l) != 0:
		for x in sorted(l, reverse=False):
			notifications.append(f"{x}")
	notifications.append(f"")



# Most wins
# Most league points won
# Total transfers made
# Most transfers made
# Biggest change in league position






### Season ###
for i in range(4): notifications.append(f"")

notifications.append(f"{n_divider}")
notifications.append(f"Season so far (to GW{gameweeks[-1]})")
notifications.append(f"{n_divider}")


# Highest overall score
m = max(d, key=lambda d: d['season_total_score'])["season_total_score"]
notifications.append(f"Most points scored: {'{:,}'.format(m)}pts")
for x in d:
	if x['season_total_score'] == m:
		notifications.append(f">> {x['manager_name']} ({x['team_name']})")
notifications.append(f"")


# Lowest overall score
m = min(d, key=lambda d: d['season_total_score'])["season_total_score"]
notifications.append(f"Fewest points scored: {'{:,}'.format(m)}pts")
for x in d:
	if x['season_total_score'] == m:
		notifications.append(f">> {x['manager_name']} ({x['team_name']})")
notifications.append(f"")


# Highest fixture score
m = max(d, key=lambda d: d['season_highest_fixture_score'])["season_highest_fixture_score"]
notifications.append(f"Highest fixture score: {'{:,}'.format(m)}pts")
for x in d:
	for idx, val in enumerate(x['season_fixture_scores']):
		if val == m:
			notifications.append(f"{'** New **' if idx+1 in gameweeks else '>>'} {x['manager_name']} ({x['team_name']}), GW{idx+1} vs {teams[x['opponents'][idx]]['team_name']}")
notifications.append(f"")


# Lowest fixture score
m = min(d, key=lambda d: d['season_lowest_fixture_score'])["season_lowest_fixture_score"]
notifications.append(f"Lowest fixture score: {'{:,}'.format(m)}pts")
for x in d:
	for idx, val in enumerate(x['season_fixture_scores']):
		if val == m:
			notifications.append(f"{'** New **' if idx+1 in gameweeks else '>>'} {x['manager_name']} ({x['team_name']}), GW{idx+1} vs {teams[x['opponents'][idx]]['team_name']}")
notifications.append(f"")



# Largest margin of victory
m = max(d, key=lambda x:x["season_highest_fixture_margin"])["season_highest_fixture_margin"]
notifications.append(f"Largest margin of victory: {'{:,}'.format(m)}pts")
for x in d:
	for idx, val in enumerate(x['season_fixture_margins']):
		if val == m:
			notifications.append(f"{'** New **' if idx+1 in gameweeks else '>>'} {x['manager_name']} ({x['team_name']}), GW{idx+1} vs {teams[x['opponents'][idx]]['team_name']}")
notifications.append(f"")


# Chips used
l = []
for x in d:
	for idx, val in enumerate(x['season_chips_played']):
		if val.lower() != "none":
			l.append(f">> {val}: {x['manager_name']} ({x['team_name']}), GW{idx+1} vs {teams[x['opponents'][idx]]['team_name']}")
notifications.append(f"Chips played: {len(l)}")
if len(l) != 0:
	for x in sorted(l):
		notifications.append(f"{x}")
notifications.append(f"")




### Print notifications ###
for n in notifications:
	print(n)


