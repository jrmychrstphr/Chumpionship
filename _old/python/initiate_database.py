from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import time
import json



fpl_home_url = "https://fantasy.premierleague.com"
league_page_url = "https://fantasy.premierleague.com/leagues/15297/standings/h"

#open Firefox
driver = webdriver.Firefox()

login_credentials = {
    "username": "jrmychrstphr@gmail.com",
    "password": "givemeaccess"
}

database = {}

#log in to fpl website
def login_to_fpl():
    
    try:

        #open the home page
        driver.get(fpl_home_url)

        #wait for the login form to appear
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "loginUsername"))
        )

        print ("Login form loaded")

    except:
        print("Failed to load page")

    #fill the form
    username_element = driver.find_element_by_id("loginUsername")
    username_element.send_keys(login_credentials["username"])
    password_element = driver.find_element_by_id("loginPassword")
    password_element.send_keys(login_credentials["password"])

    #send form
    password_element.submit()

    #wait for login
    try:
        element = WebDriverWait(driver, 10).until(
                        EC.url_changes("https://fantasy.premierleague.com/?state=success")
        )

        print (driver.current_url)
        print ("Login successful")

    except:
        print("Failed to Login")
    


# - - - - -

#CREATE A CSV FILE OF PLAYER NAMES, TEAM NAMES AND FPL Entry Number
#Might only work before GW1 is completed

def scrape_new_entries():

    #go to league page
    driver.get(league_page_url)
    
    #create soup of page DOM
    soup = BeautifulSoup(driver.page_source, 'lxml')
    #print(soup.prettify())
    
    #filter to just main page content
    main_content = soup.find(id="root")
    
    #search all 'entry' urls
    entry_anchors = soup.find_all(href=re.compile("entry"))
    
    for item in entry_anchors:
                
        #extract player name [first name / surname]
        player_name = item.text.lower().title()
        
        database[player_name] = {}
        
        player_name_lst = player_name.split(' ')
        database[player_name]["first name"] = player_name_lst[0]
        database[player_name]["surname"] = player_name_lst[1]
        
        #extract entry number
        href = item['href']
        href = href.split('/')
        database[player_name]["fpl code"] = href[2]
        
        #extract team name
        database[player_name]["team name"] = item.parent.previous_sibling.text.lower().title()
        
        #add empty dictionary for gw data
        database[player_name]["gw data"] = {}
                
        #add empty dictionary for player history
        database[player_name]["fpl history"] = {}
                
        
    print(database)
        

# - - - - -
    
def write_to_json_file(filename):
    with open(filename + '.json', 'w') as json_file:
        json.dump(database, json_file, sort_keys=True, indent=4, separators=(',', ': '))
    
    
#Execute code here
login_to_fpl()

time.sleep(1)    #blunt - needs refining

scrape_new_entries()
write_to_json_file('new')

#close browser
driver.quit()