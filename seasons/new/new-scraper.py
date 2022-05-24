from pathlib import Path

current_dir = './'
database_dir = '../database/'

entries = Path(database_dir)
for entry in entries.iterdir():
    print(entry.name)

print("")

# List all files using pathlib
files_in_basepath = entries.iterdir()
for item in files_in_basepath:
    if item.is_file():
        print(item.name)

print("")

# List all subdirectory using pathlib
for entry in entries.iterdir():
    if entry.is_dir():
        print(entry.name)

# Create a subdirectory in the same directory as the py script
p = Path('example_directory/new/new/new')
try:
    p.mkdir(parents=True)
except FileExistsError as exc:
    print(exc)

"""
Scraper:
* Open FPL league page

Compiler:
* Commit to github


Analyser

"""    