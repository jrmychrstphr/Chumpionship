"""
Takes the current information in the temp json
file and publishes it to the live file
"""

import json

f = open("../json/2020_database_temp.json")
data = json.load(f)
f.close()

with open("../json/2020_database.json", 'w') as outfile:
    json.dump(data, outfile, sort_keys=True, indent=4, separators=(',', ': '))