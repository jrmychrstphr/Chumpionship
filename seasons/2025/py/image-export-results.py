# import the required libraries
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select 


# start a driver instance
driver = webdriver.Safari()

# set the browser window size
driver.set_window_size(2000,2000)

# define a function to get scroll dimensions
def get_scroll_dimension(axis):
    return driver.execute_script(f"return document.body.parentNode.scroll{axis}")

# visit the target page
page_url = data_dir_path = f"{Path(__file__).parent.parent}/builders/viz-results.html"
driver.get('file://'+page_url)

dropdown = Select(driver.find_element(By.ID, "gameweek_select"))
options = [x.text for x in dropdown.options]
button = driver.find_element(By.ID, "controls_button")

export_dir_path = f"{Path(__file__).parent.parent}/exports/"

for idx, x in enumerate(options):
    dropdown.select_by_index(idx)
    button.click()

    fixture_gameweek = str("{0:0=2d}".format(int(x.replace("GW", ""))))
    # find the element to screenshot
    target_element = driver.find_element(By.ID, "export_me")
    # take a screenshot of the visible part
    target_element.screenshot(export_dir_path + fixture_gameweek + "-results.png")
    

# quit the driver
driver.quit()