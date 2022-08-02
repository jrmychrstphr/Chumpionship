"""
parses through all .html files in templates folder
replaces eg, {{stylesheet.css}} with the content of stylesheet.css

"""

import os
import json

from bs4 import BeautifulSoup as bs


# First pass (pulled from scraped data)
templates_directory = "./builders/~ templates"
target_directory = "./builders"

replace_list = []


for dirpath, dirnames, files in os.walk(templates_directory):
	#print(f"dirpath {dirpath}")
	#print(f"dirnames {dirnames}")
	#print(f"files {files}")

	for filename in files:
		if not filename.endswith(".html"):
			replace_list.append(filename)



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
