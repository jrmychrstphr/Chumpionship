import json
from pathlib import Path

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# *** OPEN FPL AND LOGIN **

#open Firefox
driver = webdriver.Firefox()

login_credentials = {
    "username": "jrmychrstphr@gmail.com",
    "password": "givemeaccess"
}

#log in to fpl website
def login_to_fpl():
    
    fpl_home_url = "https://fantasy.premierleague.com"
    
    try:
        #open the home page
        driver.get(fpl_home_url)
        print("FPL Website loaded")

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

        print ("login form filled")
        
        #send form
        password_element.submit()
        print ("login form submitted")

        #wait for login
        try:
            element = WebDriverWait(driver, 10).until(
                EC.url_contains("success")
            )
        
        except:
            print("Failed to Login :(")
        else: 
            print("Login successful :D")
        
login_to_fpl()


f = open("../json/2020_database.json")
data = json.load(f)
f.close()


def scrape_data():

    #gw_input = 1

    #require user input to set gameweek
    print('Enter gameweek to download:')
    gw_input = int(input())

    print(" ** Downloading data for gameweek", gw_input, "** ")
    
    url_pt1 = "https://fantasy.premierleague.com/entry/"
    url_pt2 = "/event/"
    
    for player in data:
        
        fpl_code= data[player]["fpl code"]
        print(player.title(), "(", fpl_code, ")")
            
        gw_url = str(url_pt1) + str(fpl_code) + str(url_pt2) + str(gw_input)

        try:

            #open each player's gw page on the FPL website
            driver.get(gw_url)

            #wait for element to appear
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.sc-bdVaJa.elkxqB"))
            )
            
            '''
            #wait for element to appear
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.Layout__Wrapper-eg6k6r-0"))
            )
            '''
        
            #'click' the "List View" button
            #list_view_link = driver.find_element_by_link_text('List View').click()
            driver.find_element_by_link_text('List View').click()

            #wait for the login form to appear
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table.EntryEventTable__StatsTable-sc-1d2xgo1-1"))
            )

        except:
            print(player, "– Page load error!")
        else:
            print("Page loaded successfully :D")
            print("Downloading data...")

            #create soup of page DOM
            soup = BeautifulSoup(driver.page_source, 'lxml')

            #filter to just main page content
            main_content = soup.find(id="root")

            #get points scored
            gw_final_points_title = main_content.find("h4", string="Final Points")
            gw_final_points_value = gw_final_points_title.next_sibling.text
            print("Points scored:", int(gw_final_points_value))
            
            #update points scored in database temp variable
            data[player]["gw data"][str(gw_input)]["points scored"] = int(gw_final_points_value)

            transfers_div = main_content.find("h4", string="Transfers")
            transfers_value = transfers_div.next_sibling.text

            transfers_value_split_list = transfers_value.split()

            if len(transfers_value_split_list) > 1:

                tranfers_made = transfers_value_split_list[0]
                tranfers_cost = transfers_value_split_list[1].replace("(","")

            else:

                tranfers_made = transfers_value_split_list[0]
                tranfers_cost = 0

            print("Tranfers made:", tranfers_made)
            print("Points spent:", tranfers_cost)    

            data[player]["gw data"][str(gw_input)]["transfers made"] = int(tranfers_made)
            data[player]["gw data"][str(gw_input)]["points spent"] = int(tranfers_cost)*-1

            #calculate fixture score
            data[player]["gw data"][str(gw_input)]["fixture total"] = (data[player]["gw data"][str(gw_input)]["points scored"])-(data[player]["gw data"][str(gw_input)]["points spent"])

            print("Fixture total:", data[player]["gw data"][str(gw_input)]["fixture total"])    
            
            
            #get chip played
            gw_chip_played_div_list = main_content.select("div.EntryEvent__ChipStatus-l17rqm-15.csGQqo")
            
            if len(gw_chip_played_div_list) > 0:
                
                
                if len(gw_chip_played_div_list) == 1:
                    
                    print("A chip was played!")

                    for idx, chip_div in enumerate(gw_chip_played_div_list):
                        print(chip_div.text)
                        chip_string = chip_div.text
                        
                        chip = ""
                        
                        if "Triple Captain" in chip_string:
                            print("Triple Captain played")
                            chip = "Triple Captain"
                        
                        elif "Bench Boost" in chip_string:
                            print("Bench Boost played")
                            chip = "Bench Boost"
                            
                        elif "Wildcard" in chip_string:
                            print("Wildcard played")
                            
                                                        
                        elif "Free Hit" in chip_string:
                            print("Free Hit played")
                            chip = "Free Hit"
                            
                        else:
                            print("Unable to determine which chip was played!")
                            print('Press enter to continue:')
                            input()
                        
                        data[player]["gw data"][str(gw_input)]["chip played"] = chip
                        
                else:
                    
                        print('HELP! Multiple chip divs found!')
                        print('Press enter to continue:')
                        input()

                    
            else:
                print("No chip played!")
                
                

            #find stats tables for player data
            stats_tables = main_content.find_all("table", class_="EntryEventTable__StatsTable-sc-1d2xgo1-1")

            print("Downloading squad data...")

            # for each table:
            for table_idx,table in enumerate(stats_tables):

                #create an array/list to store table head titles
                keys = []

                table_soup = stats_tables[table_idx]
                table_head = table_soup.find("thead")
                table_body = table_soup.find("tbody")

                table_head_cells = table_head.find_all("th")

                #create a list of key names based on table head
                for cell in table_head_cells:
                    if "abbr" in str(cell):
                        keys.append(cell.abbr["title"].lower())
                    else:
                        keys.append(cell.text.lower())

                player_status = keys[2].lower() #define starters / substitutes

                print(player_status.title())

                table_rows = table_body.find_all("tr")

                data[player]["gw data"][str(gw_input)]["squad"][str(player_status)] = {}

                if player_status == "starters":
                    formation_count = {"GKP": 0, "DEF": 0, "MID": 0, "FWD": 0}

                #for each row in  the table...
                for row_idx,row in enumerate(table_rows):

                    data[player]["gw data"][str(gw_input)]["squad"][str(player_status)][str(int(row_idx)+1)] = {}

                    data[player]["gw data"][str(gw_input)]["squad"][str(player_status)][str(int(row_idx)+1)]["stats"] = {}

                    row_soup = table_rows[row_idx]
                    row_cells = row_soup.find_all("td")

                    for cell_idx,cell in enumerate(row_cells):

                        if cell_idx != 0 :   #ignore first column - info button


                            if cell_idx == 1:    #check if captain/vice

                                vc_class = "TableCaptains__StyledViceCaptain-sc-1ub910p-1"
                                cap_class = "TableCaptains__StyledCaptain-sc-1ub910p-0"


                                captain_status = ""

                                if vc_class in str(cell):
                                    captain_status = "Vice Captain"
                                elif cap_class in str(cell):
                                    captain_status = "Captain"
                                else:
                                    captain_status = "None"

                                data[player]["gw data"][str(gw_input)]["squad"][str(player_status)][str(int(row_idx)+1)]["captain status"] = str(captain_status)

                            elif cell_idx == 2:  #get player name / team / position

                                name_div = cell.find("div", class_="ElementInTable__Name-y9xi40-1")

                                team_pos_div = name_div.next_sibling
                                team_pos_div_spans = team_pos_div.find_all("span")

                                team_code = team_pos_div_spans[0].text
                                pos_code = team_pos_div_spans[1].text

                                data[player]["gw data"][str(gw_input)]["squad"][str(player_status)][str(int(row_idx)+1)]["name"] = str(name_div.text)

                                print(row_idx+1, "–", str(name_div.text).title(), team_code, pos_code)

                                data[player]["gw data"][str(gw_input)]["squad"][str(player_status)][str(int(row_idx)+1)]["team"] = str(team_code)

                                data[player]["gw data"][str(gw_input)]["squad"][str(player_status)][str(int(row_idx)+1)]["position"] = str(pos_code)

                                if player_status == "starters":
                                    formation_count[pos_code] = int(formation_count[pos_code])+1


                            else:  #get all other data points, key = table heading

                                data[player]["gw data"][str(gw_input)]["squad"][str(player_status)][str(int(row_idx)+1)]["stats"][str(keys[cell_idx])] = float(cell.text)

                        data[player]["gw data"][str(gw_input)]["formation"] = str(formation_count["DEF"]) + "-" + str(formation_count["MID"]) + "-" + str(formation_count["FWD"])                                     


    # THINGS TO DO:

    # – calculate fixture results (i.e. compare fixture scores) (+)
    # – calculate overall total (+)
    # – calculate total league points (+)
    
    
    # - calculate points scored breakdown per position (GKP, DEF, MID, FWD)
    # – calculate longest/current win/winless streaks
    
    print("Compiling fixture results and season totals...")
    #cycle through each player and...
    for player in data:
        
        print(player.title())
        
        # compare scores with opponent to determin fixture result
        opponent = data[player]["gw data"][str(gw_input)]["opponent"]

        player_score = data[player]["gw data"][str(gw_input)]["fixture total"]
        opponent_score = data[opponent.lower()]["gw data"][str(gw_input)]["fixture total"]

        print(player.title(), player_score, ":", opponent_score, opponent.title())

        if player_score > opponent_score:
            print(player.title(), "wins :D")
            data[player]["gw data"][str(gw_input)]["fixture result"] = "win"
        elif player_score < opponent_score:
            print(player.title(), "loses D:")
            data[player]["gw data"][str(gw_input)]["fixture result"] = "loss"
        elif player_score == opponent_score:
            print(player.title(), "draws")
            data[player]["gw data"][str(gw_input)]["fixture result"] = "draw"
        else:
            print("Error compiling fixture result!")            
        
        
        score_count = 0
        transfers_count = 0
        spend_count = 0
        league_points_count = 0
        
        #add up fixture total / points spent / transfers made to date
        for x in range(1, gw_input+1):
            score_count = score_count + data[player]["gw data"][str(x)]["points scored"]
            transfers_count = transfers_count + data[player]["gw data"][str(x)]["transfers made"]
            spend_count = spend_count + data[player]["gw data"][str(x)]["points spent"]

            fixture_result = data[player]["gw data"][str(x)]["fixture result"]

            if fixture_result == "win":
                league_points_count = league_points_count + 3
            elif fixture_result == "draw":
                league_points_count = league_points_count + 1
            elif fixture_result == "loss":
                league_points_count = league_points_count + 0
            else:
                print("Error in calculating league points gained in gw", x)
                
        #update the data -- DO THIS ONLY ONCE!
        data[player]["total points scored"] = score_count
        data[player]["total points spent"] = spend_count
        data[player]["overall points"] = score_count - spend_count
        data[player]["total league points"] = league_points_count
        data[player]["total transfers made"] = transfers_count

        print("total transfers made:", transfers_count)

        print("total points scored:", score_count)
        print("total points spent:", spend_count)
        print("overall score:", score_count - spend_count)

        print("total league points:", league_points_count)        
        
        

    with open("../json/2020_database_temp.json", 'w') as outfile:
        print("Exporting data to file: '../json/2020_database_temp.json'")
        json.dump(data, outfile, sort_keys=True, indent=4, separators=(',', ': '))
        
scrape_data()    
    
#close browser
driver.quit()


print(" ** Complete ** ")
    
    