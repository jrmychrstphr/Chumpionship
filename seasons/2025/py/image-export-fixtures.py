# import the required libraries
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import Select 

# start a WebDriver instance
driver = webdriver.Safari()

# maximizing browser
driver.maximize_window() 

# visit the target page
page_url = data_dir_path = f"{Path(__file__).parent.parent}/builders/viz-fixture-list.html"
driver.get('file://'+page_url)

dropdown = Select(driver.find_element(By.ID, "gameweek_select"))
options = [x.text for x in dropdown.options]
button = driver.find_element(By.ID, "controls_button")

print(options)

dropdown.select_by_visible_text(options[0])
button.click()

import time

export_dir_path = f"{Path(__file__).parent.parent}/exports/"

for idx, x in enumerate(options):
    dropdown.select_by_index(idx)
    button.click()
    fixture_gameweek = str("{0:0=2d}".format(int(x.replace("GW", ""))))
    # find the element to screenshot
    target_element = driver.find_element(By.ID, "export_me")
    # take a screenshot of the visible part
    target_element.screenshot(export_dir_path + fixture_gameweek + "-fixtures.png")
    

# quit the driver
driver.quit()