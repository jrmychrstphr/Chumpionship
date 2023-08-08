from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def accept_cookies(driver):

	completed = False

	#open the webpage
	driver.get("https://fantasy.premierleague.com/")

	while completed == False:
		
		accept_btn_css_selector = "#onetrust-accept-btn-handler"

		try:
			print("Waiting to accept cookies")
			# wait for the 'accept all' button to be clickable
			WebDriverWait(driver, 30).until(
				EC.element_to_be_clickable((By.CSS_SELECTOR, accept_btn_css_selector))
			)
		
		#if that fails, try again?
		except:
			input_check = input("Button not found. Try again? (Y): ")
			if str(input_check.upper()) == "Y":
				continue
			else:
				break
		
		#if the button is dfound, let's click it!
		else:
			# Click the button
			driver.find_element_by_css_selector(accept_btn_css_selector).click()
			print("Button clicked - cookies accepted")
			completed = True

