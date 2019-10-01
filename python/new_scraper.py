import json
from pathlib import Path

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import operator


###############
# Set global variables #

#FPL login credentials
login_credentials = {
    "username": "jrmychrstphr@gmail.com",
    "password": "givemeaccess"
}

#URLs
fpl_home_url = "https://fantasy.premierleague.com"

###############
# Load the database #

f = open("../json/2020_database.json")
data = json.load(f)
f.close()

# Temporary object to hold new database
## Not currently used ##
temp_data = data


###############
# User input #

def user_input():
    
    global update_all_boolean
    global gw_input
    global reset_gw_data_boolean
    reset_gw_data_boolean = False
    
    #Define update_all
    print('Update all? (Y/N)')
    update_input = str(input())
    
    if update_input.upper() == "Y":
        update_all_boolean = True
    else:
        update_all_boolean = False
        
    print("Update all set to:", update_all_boolean)
        

    #Define the GW
    if update_all_boolean == True:
        print('Enter gameweek to download up to:')
    else:
        print('Enter gameweek to download:')
        
    gw_input = int(input())
    print("GW set to:", gw_input)
    
    '''
    #Define reset_gw_data
    print('Reset GW data? (Y/N)')
    reset_input = str(input())
    
    if reset_input.upper() == "Y":
        reset_gw_data_boolean = True
    else:
        reset_gw_data_boolean = False
    '''    
        
    print("Reset GWs set to:", reset_gw_data_boolean)


###############
# Load and log in to FPL website #

def login_to_fpl():  
        
    try:
        #open the home page
        driver.get(fpl_home_url)
        print("FPL Website loaded")

        #wait for the login form to appear
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "loginUsername"))
        )
        
    except:
        #if the website fails to load, display an error message
        print("Error: login form didn't load")
    
    else:
        
        #after the login form laods:
        
        #fill the form
        username_element = driver.find_element_by_id("loginUsername")
        username_element.send_keys(login_credentials["username"])
        password_element = driver.find_element_by_id("loginPassword")
        password_element.send_keys(login_credentials["password"])

        print ("login form has been filled filled")
        
        #send form
        password_element.submit()
        print ("login form submitted")

        #wait for login
        try:
            element = WebDriverWait(driver, 10).until(
                EC.url_contains("success")
            )
        
        except:
            #if login fails, display an error message
            print("Error: failed to Login :(")
        else: 
            #if login is successful, display success message
            print("Success: logged in to FPL :D")


###############
# Scrape data #

def scrape(gw):

    print("Downloading data for gameweek", gw)
    
    url_pt1 = "https://fantasy.premierleague.com/entry/"
    url_pt2 = "/event/"
    
    # loop through each top-level object in the database (players)
    for player in data:
        
        fpl_code= data[player]["fpl code"]
        print(player.title(), "(", fpl_code, ")")
            
        gw_url = str(url_pt1) + str(fpl_code) + str(url_pt2) + str(gw)

        try:

            #open the player's gw page on the FPL website
            driver.get(gw_url)

            #wait for element to appear
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.sc-bdVaJa.elkxqB"))
            )
        
            #'click' the "List View" button to load data table
            driver.find_element_by_link_text('List View').click()

            #wait for the data table to appear
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table.EntryEventTable__StatsTable-sc-1d2xgo1-1"))
            )

        except:
            #if the data table fails to load, display an error message
            print(player, " – Error: Data table failed to load :( – GW", gw)
        else:
            
            print("Page loaded successfully :D")
            print("Downloading data...")

            #create soup of page DOM
            soup = BeautifulSoup(driver.page_source, 'lxml')

            #filter to just main page content
            page_content = soup.find(id="root")

            #get points scored from main page display
            gw_final_points_title_div = page_content.find("h4", string="Final Points")
            gw_final_points_value_text = gw_final_points_title_div.next_sibling.text
            gw_final_points_value = int(gw_final_points_value_text)
            print("Points scored:", gw_final_points_value)
            
            
            ####
            # I want to compare this against the player points 
            # before updating the database at some point too
            ####
            
            if str(gw) in data[player]["gw data"].keys():
                print("key found:", str(gw))
            else:
                print("key not found:", str(gw))
                print(data[player]["gw data"])
                data[player]["gw data"][str(gw)] = {}
                print(data[player]["gw data"])
            
            
            #update points scored in database temp variable
            data[player]["gw data"][str(gw)]["points scored"] = gw_final_points_value

            
            # Scrape transfers made and points spent
            
            ####
            # This can later be done via the Gameweek History 
            # and/or the Transfers History page
            ####
            
            
            transfers_div = page_content.find("h4", string="Transfers")
            transfers_value_text = transfers_div.next_sibling.text

            #'split' the text string in to a list (array) of separate words
            transfers_value_text_split_list = transfers_value_text.split()

            # if the 'split' array returns with more than one item, this indicates there is a transfer cost
            if len(transfers_value_text_split_list) > 1:
                tranfers_made_value = int(transfers_value_text_split_list[0])
                tranfers_cost_value = int(transfers_value_text_split_list[1].replace("(",""))*-1
            else:
                tranfers_made_value = int(transfers_value_text_split_list[0])
                tranfers_cost_value = 0

            print("Tranfers made:", tranfers_made_value)
            print("Points spent:", tranfers_cost_value)    

            data[player]["gw data"][str(gw)]["transfers made"] = tranfers_made_value
            data[player]["gw data"][str(gw)]["points spent"] = tranfers_cost_value

            #calculate fixture total (points scored minus points spent)
            fixture_total = gw_final_points_value - tranfers_cost_value
            
            data[player]["gw data"][str(gw)]["fixture total"] = fixture_total

            print("Fixture total:", fixture_total)    
            
            
            #Search the soup for the 'chip played' display element
            gw_chip_played_div_list = page_content.select("div.EntryEvent__ChipStatus-l17rqm-15.csGQqo")
            
            #This will return a list (array) of all divs in the soup with the specified css class
            
            #If the list is not empty, this indicates that a chip was played
            if len(gw_chip_played_div_list) > 0:
                
                #Fingers crossed that this list is only 1 item long! 
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
                        
                        data[player]["gw data"][str(gw)]["chip played"] = chip  #can I move this?
                
                #if the list is longer than 1, why?
                else:
                    
                        print('HELP! Multiple chip divs found!')
                        print('Press enter to continue:')
                        input() #pause script for review
                        
            # if the list returned is empty, this indicates that no chip was played        
            else:
                print("No chip played!")
                
            
                
                
            #Search the soup for stats tables containing player data (there should be two of these)
            stats_tables = page_content.find_all("table", class_="EntryEventTable__StatsTable-sc-1d2xgo1-1")

            print("Downloading squad data...")

            #Failsafe for catching if a total of two tables are not returned
            if len(stats_tables) != 2:
                
                print("HELP! Search for player dfata tables returned an unexpected number of results" )
                print("Number of results:",  len(stats_tables))
                print('Press enter to continue:')
                input() #pause script for review
                
            else:
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
                    
                    if "squad" in data[player]["gw data"][str(gw)].keys():
                        print("key found:", "squad")
                    else:
                        print("key not found:", "squad")
                        print(data[player]["gw data"][str(gw)])
                        data[player]["gw data"][str(gw)]["squad"] = {}
                        print(data[player]["gw data"][str(gw)])

                    data[player]["gw data"][str(gw)]["squad"][str(player_status)] = {}    #create an empty dictionary to hold player data

                    if player_status == "starters":
                        formation_count = {"GKP": 0, "DEF": 0, "MID": 0, "FWD": 0}

                    #for each row in  the table...
                    for row_idx,row in enumerate(table_rows):

                        data[player]["gw data"][str(gw)]["squad"][str(player_status)][str(int(row_idx)+1)] = {}

                        data[player]["gw data"][str(gw)]["squad"][str(player_status)][str(int(row_idx)+1)]["stats"] = {}

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

                                    data[player]["gw data"][str(gw)]["squad"][str(player_status)][str(int(row_idx)+1)]["captain status"] = str(captain_status)

                                elif cell_idx == 2:  #get player name / team / position

                                    name_div = cell.find("div", class_="ElementInTable__Name-y9xi40-1")

                                    team_pos_div = name_div.next_sibling
                                    team_pos_div_spans = team_pos_div.find_all("span")

                                    team_code = team_pos_div_spans[0].text
                                    pos_code = team_pos_div_spans[1].text

                                    data[player]["gw data"][str(gw)]["squad"][str(player_status)][str(int(row_idx)+1)]["name"] = str(name_div.text)

                                    print(row_idx+1, "–", str(name_div.text).title(), team_code, pos_code)

                                    data[player]["gw data"][str(gw)]["squad"][str(player_status)][str(int(row_idx)+1)]["team"] = str(team_code)

                                    data[player]["gw data"][str(gw)]["squad"][str(player_status)][str(int(row_idx)+1)]["position"] = str(pos_code)

                                    if player_status == "starters":
                                        formation_count[pos_code] = int(formation_count[pos_code])+1


                                else:  #get all other data points, key = table heading

                                    data[player]["gw data"][str(gw)]["squad"][str(player_status)][str(int(row_idx)+1)]["stats"][str(keys[cell_idx])] = float(cell.text)
                                    
                            data[player]["gw data"][str(gw)]["formation"] = str(formation_count["DEF"]) + "-" + str(formation_count["MID"]) + "-" + str(formation_count["FWD"])

###############
# Analyse gameweek data #

## Formation analysis (currently in scrape()) should move here

def analyse_gw(gw):
    
    print("Analysing data for gameweek", gw)
    
    # loop through each top-level object in the database (players)
    for player in data:
                
        print(player.title())
                
        # Compare scores with opponent to determine fixture result
        
        opponent = data[player]["gw data"][str(gw)]["opponent"]
        
        player_score = data[player]["gw data"][str(gw)]["fixture total"]
        opponent_score = data[opponent.lower()]["gw data"][str(gw)]["fixture total"]

        print(player.title(), player_score, ":", opponent_score, opponent.title())

        if player_score > opponent_score:
            print(player.title(), "wins :D")
            result = "win"
        elif player_score < opponent_score:
            print(player.title(), "loses D:")
            result = "loss"
        elif player_score == opponent_score:
            print(player.title(), "draws")
            result = "draw"
        else:
            print("Error compiling fixture result!")
            
        data[player]["gw data"][str(gw)]["fixture result"] = result
        data[player]["gw data"][str(gw)]["points against"] = opponent_score
        
        
###############
# Analyse overall data #

def analyse_overall():
    
    print("Analysing overall data")
    
    # loop through each top-level object in the database (players)
    for player in data:
        print(player.title())
        
        #reset counters
        score_count = 0
        points_against_count = 0    #add points against to the scrape()
        transfers_count = 0
        spend_count = 0
        league_points_count = 0
        win_count = 0
        draw_count = 0
        loss_count = 0
        
        formations_count = {}
        chips_played_count = {}
        
        gameweeks_played = len(data[player]["gw data"])
        
        formations_used = []
        formations_list = []
        
        #for every gameweek with data...
        for x in range(1, gameweeks_played+1):
            
            def return_key_if_it_exists(key):
                if key in data[player]["gw data"][str(x)].keys():
                    return int(data[player]["gw data"][str(x)][str(key)])
                else:
                    print(str(key), "does not exist")
                    return 0
                    
            score_count += return_key_if_it_exists("points scored")
            transfers_count += return_key_if_it_exists("transfers made")
            spend_count += return_key_if_it_exists("points spent")
            points_against_count += return_key_if_it_exists("points against")
            
            '''
            score_count += data[player]["gw data"][str(x)]["points scored"]
            transfers_count += data[player]["gw data"][str(x)]["transfers made"]
            spend_count += data[player]["gw data"][str(x)]["points spent"]
            points_against_count += data[player]["gw data"][str(x)]["points against"]
            '''

            fixture_result = data[player]["gw data"][str(x)]["fixture result"]

            if fixture_result == "win":
                league_points_count +=  3
                win_count += 1
                
            elif fixture_result == "draw":
                league_points_count += 1
                draw_count += 1
                
            elif fixture_result == "loss":
                league_points_count += 0
                loss_count += 1
                
            else:
                print("Error in reading result in gw", x)
            
            #
            if "formation" in data[player]["gw data"][str(x)]:
                
                formation_played = data[player]["gw data"][str(x)]["formation"]
                formations_list.append(formation_played)
            
                if formation_played in formations_used == False:
                    formations_used.append(formation_played)
            
                
        #Update the data -- DO THIS ONLY ONCE!
        data[player]["total points scored"] = score_count
        data[player]["total points against"] = points_against_count
        data[player]["total points spent"] = spend_count
        data[player]["overall points"] = score_count - spend_count
        data[player]["total league points"] = league_points_count
        data[player]["total transfers made"] = transfers_count
        
        data[player]["formations"] = {}
        
        for formation in formations_used:
            data[player]["formations"][formation] = int(formations_list.count(formation))
        
        data[player]["results"] = {}
        data[player]["results"]["win"] = int(win_count)
        data[player]["results"]["draw"] = int(draw_count)
        data[player]["results"]["loss"] = int(loss_count)

        print("total transfers made:", transfers_count)
        print("total points scored:", score_count)
        print("total points spent:", spend_count)
        print("overall score:", score_count - spend_count)
        print("total league points:", league_points_count)
    
    #Calculate overall league positions
    def calculate_overall_league_position():
        print("Calculating league positions")
        table_list = []

        # create a sortable list
        for player in data:
            player_list = []

            player_list.insert(0, player)                         #0 - player name
            player_list.insert(1, data[player]["team name"])              #1 - team name
            player_list.insert(2, data[player]["overall points"])         #2 - overall points
            player_list.insert(3, data[player]["total league points"])    #3 - league points

            table_list.append(player_list)

        #sort the list
        table_list = sorted(table_list, key = lambda x: (x[3]*-1, x[2]*-1, x[1]))

        #cycle through sorted list and define league position
        #including if there are equally positioned teams 
        #(i.e. same points and score)
        for idx,item in enumerate(table_list):

            prev_position = 0
            prev_score = 0
            prev_points = 0

            position = 0

            if idx == 0:
                position = idx + 1
                previous_position = idx + 1

            else:
                if previous_points == table_list[idx][3] and previous_score == table_list[idx][2]:
                    position = previous_position
                else:
                    position = idx + 1
                    previous_position = idx + 1

            previous_score = table_list[idx][2]
            previous_points = table_list[idx][3]

            print("#" + str(position), table_list[idx][1].title(), table_list[idx][2], table_list[idx][3])
            
            data[table_list[idx][0]]["league position"] = int(position)

        ######################
        #To add: 
        #   - check against FPL site table

    calculate_overall_league_position()        
        
    ######################
    #To add: 
    #- League position every gameweek
    #- Finish formation count analysis
        
        
def reset_gw_data():
    for player in data:
        data[player]["gw data"] = {}
    print("GW data reset")
        
        
###############
# Write new data to temp file #

def update_database():
    
    filename = "../json/2020_database_temp.json"
    
    with open(filename, 'w') as outfile:
        print("Exporting data to file:", filename)
        json.dump(data, outfile, sort_keys=True, indent=4, separators=(',', ': '))

        
###############
# Open browser #

def open_browser():
    # Open browser
    global driver
    driver = webdriver.Firefox()
    print("Browser opened")

    
###############
# Close browser #

def close_browser():
    #close browser
    driver.quit()
    print("Browser closed")

    
    
###############
# Execute code here #
def main():
    
    user_input()    #prompt user input
    
    #print("update_all_boolean: ", update_all_boolean)
    #print("gw_input: ", gw_input)
    #print("reset_gw_data_boolean: ", reset_gw_data_boolean)

    open_browser()
    login_to_fpl()

    
    #optional hard reset of GW data
    if reset_gw_data_boolean == True:
        reset_gw_data()
        print("GW data has been reset")
    else: 
        print("GW data was not reset")
        print("Boolean value:", reset_gw_data_boolean)

        
    #if user decides to only scrape single GW...
    if update_all_boolean == False:

        scrape(gw_input)
        analyse_gw(gw_input)
        analyse_overall()

    #if user input decides to update all GWs...
    elif update_all_boolean == True:

        #scrape and analyse each gw in turn
        for x in range(1, gw_input+1):
            scrape(x)
            analyse_gw(x)

        #then analyse overall data
        analyse_overall()

    else:
        print("HELP! Something went wrong!!")

        
    driver.quit()
    update_database()
    
main()

print(" ** Complete ** ")
    
    