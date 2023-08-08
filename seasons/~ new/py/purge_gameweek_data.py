from pathlib import Path
import os


def purge():

	database_dir = "../data"

	for dirpath, dirnames, files in os.walk(database_dir):
		print(f"Found directory: {dirpath}")

		for file_name in files:

			if file_name.startswith("GW"):

				#print('1', dirpath)
				#print('2', file_name)
				#print('3', dirpath + file_name)

				f = dirpath + "/" + file_name
				print(f"Deleted: {f}")
				os.remove(f)

def execute():

	input_verified = False

	while input_verified == False:

		print("You are about to purge the database of all gameweek data")
		input_check_a = str(input("Do you wish to proceed? (Y):").upper())
		input_check_b = str(input('Are you sure? (Y):').upper())

		if input_check_a == "Y" and input_check_b == "Y":
			purge()
			print("Database purged")
			input_verified = True
			break
		else:
			continue

execute()