# ============================================================
# This script parses through all .html files in templates folder
# and replaces eg, **stylesheet.css** with the content of stylesheet.css
# ============================================================


import os
import json

from bs4 import BeautifulSoup as bs
from pathlib import Path


data_dir_path = f"{Path(__file__).parent.parent}/data"
builder_dir_path = f"{Path(__file__).parent.parent}/builders"
templates_dir_path = f"{Path(__file__).parent.parent}/builders/~ templates"

database_file_path = f"{Path(__file__).parent.parent}/data/database.json"
fixtures_file_path = f"{Path(__file__).parent.parent}/data/season_fixture_list.json"


list_of_templates_folder_contents = os.listdir(templates_dir_path)

list_of_other_files = [x for x in list_of_templates_folder_contents if not x.endswith(".html")]
list_of_html_files = [x for x in list_of_templates_folder_contents if x.endswith(".html")]

print(f"other: {list_of_other_files}")
print(f"html: {list_of_html_files}")


for filename in list_of_html_files:
	with open(templates_dir_path + "/" + filename) as html:
		html = html.read()
		print(filename)

		for x in list_of_other_files:
			string_to_replace = "**"+x+"**"
			if string_to_replace in html:
				print(string_to_replace)
				with open(templates_dir_path + "/" + x) as r:
					r = str(r.read())
					html = html.replace(string_to_replace, r)

		if "**database.json**" in html:
			with open(database_file_path) as r:
				print("**database.json**")
				r = str(r.read())
				html = html.replace("**database.json**", r)

		if "**fixture-list.json**" in html or "**season_fixture_list.json**" in html:
			print("**fixture-list.json**")
			with open(fixtures_file_path) as r:
				r = str(r.read())
				html = html.replace("**fixture-list.json**", r)

		with open(builder_dir_path + "/" + filename, "w") as f:
			soup = bs(html, "html.parser")
			html = soup.prettify()
			f.write(html)

	print("")
