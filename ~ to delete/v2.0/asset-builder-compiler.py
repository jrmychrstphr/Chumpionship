"""
parses through all .html files in templates folder
replaces eg, {{stylesheet.css}} with the content of stylesheet.css

"""

import os
import json

from bs4 import BeautifulSoup as bs


# First pass (pulled from scraped data)
templates_directory = "asset-builder-templates"
target_directory = "asset-builders"

replace_list = [
	"chumpionship-styles.css",
	"common_functions.js",	
	"database_queries.js",
	"content-builders-library.js",
	"chumpionship_colours.js",
    "svg.js",
    "dynamic_styles.js",
    "load_database.js", 
    "database.json",
    "fixture_list.json"
    ]

for dirpath, dirnames, files in os.walk(templates_directory):
	#print(f"dirpath {dirpath}")
	#print(f"dirnames {dirnames}")
	#print(f"files {files}")

	for filename in files:
		if filename.endswith(".html"):
			print(filename)
			with open(templates_directory + "/" + filename) as html:
				html = html.read()
				#print(html)

				for x in replace_list:
					string_to_replace = "**"+x+"**"
					if string_to_replace in html:
						print(string_to_replace)
						with open(templates_directory + "/" + x) as r:
							r = str(r.read())
							html = html.replace(string_to_replace, r)


				with open(target_directory + "/" + filename, "w") as f:
					soup = bs(html, "html.parser")
					html = soup.prettify()
					f.write(html)

			print("")
