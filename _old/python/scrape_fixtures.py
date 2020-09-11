import json
from pathlib import Path

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Open the fpl website and login
fpl_home_url = "https://fantasy.premierleague.com"
league_page_url = "https://fantasy.premierleague.com/leagues/15297/standings/h"
league_fixture_url = "https://fantasy.premierleague.com/leagues/15297/matches/h?entry="

# *** OPEN FPL AND LOGIN **

#open Firefox
driver = webdriver.Firefox()

login_credentials = {
    "username": "jrmychrstphr@gmail.com",
    "password": "givemeaccess"
}

#log in to fpl website
def login_to_fpl():
    
    try:
        #open the home page
        driver.get(fpl_home_url)

        #wait for the login form to appear
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "loginUsername"))
        )
        
    except:
        print("Login form didn't load")
    
    else:
        #fill the form
        username_element = driver.find_element_by_id("loginUsername")
        username_element.send_keys(login_credentials["username"])
        password_element = driver.find_element_by_id("loginPassword")
        password_element.send_keys(login_credentials["password"])

        print (driver.current_url)
        
        #send form
        password_element.submit()

        #wait for login
        try:
            element = WebDriverWait(driver, 10).until(
                EC.url_contains("success")
            )
        
        except:
            print("Failed to Login")
        else: 
            print("the url changed")
            print (driver.current_url)
        
login_to_fpl()

# *** LOAD THE 2020 DATABASE JSON FILE ***
    

# – – – – – –
# Iterate through each player and scrape their fixtures
# – – – – – –

def scrape_fixtures():
    
    # Load 2020 database
    with open("../json/2020_database.json") as json_file:
        data = json.load(json_file)
        
        print(data)
    
        for player in data:
            fpl_code= data[player]["fpl code"]
            
            
            try:
                #open each player's fixture page on the FPL website
                driver.get(league_fixture_url+fpl_code)
                
                #wait for the login form to appear
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "table.MatchesTable-sc-1p0h4g1-0"))
                )
                
            except:
                print(player, "Something went wrong")
            else:
                print(player, "Success")

                #create soup of page DOM
                soup = BeautifulSoup(driver.page_source, 'lxml')

                #filter to just main page content
                main_content = soup.find(id="root")

                #search for the fixtures table element
                table = main_content.find("table", class_="MatchesTable-sc-1p0h4g1-0")
                
                #refine this to just the body
                table_rows = table.find_all("tr")

                for x in table_rows:
                    
                    if "</td>" in str(x.contents[0]):
                        
                        #find the gameweek
                        string_start = "<td>"
                        string_start_pos = str(x.contents[0]).find(string_start)
                        string_start_pos = string_start_pos + len(string_start)
                        #print("string_start", string_start_pos)

                        string_end_pos = str(x.contents[0]).find("</td>")
                        #print("string_end", string_end_pos)

                        string = str(x.contents[0])[string_start_pos:string_end_pos]
                        #print(string)
                        
                        gw = string

                        #find player name 1
                        string_start = "</strong><br/>"
                        string_start_pos = str(x.contents[1]).find(string_start)
                        string_start_pos = string_start_pos + len(string_start)
                        #print("string_start", string_start_pos)

                        string_end_pos = str(x.contents[1]).find("</td>")
                        #print("string_end", string_end_pos)

                        string = str(x.contents[1])[string_start_pos:string_end_pos]
                        
                        #remove rogue <a/> tags
                        if "</a>" in string.lower():
                            string = string.replace("</a>", "")
                            
                        #Gareth M fix
                        if "gareth m" in string.lower():
                            string = string + "ytton"
                            
                        #print(string)
                        
                        if string.lower() != player.lower():
                            opponent = string
                        else:
                            #find player name 2
                            string_start = "</strong><br/>"
                            string_start_pos = str(x.contents[3]).find(string_start)
                            string_start_pos = string_start_pos + len(string_start)
                            #print("string_start", string_start_pos)

                            string_end_pos = str(x.contents[3]).find("</td>")
                            #print("string_end", string_end_pos)

                            string = str(x.contents[3])[string_start_pos:string_end_pos]
                            #print(string)
                            
                            #remove rogue <a/> tags
                            if "</a>" in string.lower():
                                string = string.replace("</a>", "")

                            #Gareth M fix
                            if "gareth m" in string.lower():
                                string = string + "ytton"
                            
                            opponent = string.title()
                            
                        print(player, "gw", gw, "opponent", opponent)
                        
                        data[player]["gw data"][gw]["opponent"] = opponent
                        
                                
                        with open("../json/2020_database_temp.json", 'w') as outfile:
                            json.dump(data, outfile, sort_keys=True, indent=4, separators=(',', ': '))
                        
scrape_fixtures()

#close browser
driver.quit()

print("Complete")