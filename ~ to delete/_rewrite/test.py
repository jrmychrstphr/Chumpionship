import json
from pathlib import Path

def return_load_json_file(filename):

	print("Loading file... ", filename)

	try:
		f = open(filename)
		json_data = json.load(f)
		f.close()

	except:
		print("Error... failed to load file")
	else:
		print("Success!")
		return json_data


def covid_fix(input_data):

	# takes gw_performance data (input_data)
	# removes data for GW30 - 38 
	# replaces with data from GW39 - 47 if it exists

	print("Covid fix started...")

	output_data = {}

	# remove data for GW30+ from output

	# for each item (keys = manager_code) in the dict 
	for manager_code, data in input_data.items():

		print("manager_code... ", manager_code)

		output_data[manager_code] = {}
		lockdown_transfers = 0

		# input pass 1 -- collect lockdown data
		print("Pass 1")
		for gw, v in data.items():

			# if gw is between 30 and 38, this is a lockdown gameweek
			# Collect transfers made data and add to lockdown_transfers
			if int(gw) > 29 and int(gw) < 39:
				lockdown_transfers += v['transfers_made']


		# input pass 2 -- replace data
		print("Pass 2")
		for gw, v in data.items():

			# if gw is 1 - 29, this doesn't need to be fixed
			# so, copy the data as is
			if int(gw) < 30:
				output_data[manager_code][gw] = v

			# if gw is 39+, transpose to 9 rounds sooner
			# e.g. 39 = 30 // 40 = 31 
			elif int(gw) > 38:
				gameweek_to = str("{0:0=2d}".format(int(gw)-9))
				output_data[manager_code][gameweek_to] = input_data[manager_code][gw]

		print("Additional gamweek data transposed")

		# add lockdown transfers to first round or the restart (gw 30)
		output_data[manager_code]['30']['transfers_made'] += lockdown_transfers
		print("Lockdown data added to GW30")

	print("Covid fix complete...")
	return output_data



def execute():
	global gw_performance_data
	gw_performance_data = return_load_json_file('gw_performance_data---20200618_0857.json')

	gw_performance_data = covid_fix(gw_performance_data)
	print(gw_performance_data)


execute()