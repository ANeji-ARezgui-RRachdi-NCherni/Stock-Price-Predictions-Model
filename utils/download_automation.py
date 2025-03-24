from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

#constants
LINK =  "https://www.ilboursa.com/marches/download/"
START_DATE = "01/01/2010"

# browser webdriver
edgedriver_path = "C:/Users/rezgu/webdriver/msedgedriver.exe"

# Set up EdgeDriver
service = Service(executable_path=edgedriver_path)
driver = webdriver.Edge(service=service)

# Stock Symbols
links=[
    "HL","GIF","ECYCL","SOKNA","NAKL","LSTR","ELBEN","DH","CITY","SCB","CIL","CREAL",
    "CELL","CC","BTE","BIAT","BHL","BH","BHASS","BL","BNA","BT","TJARI","TJL","AST",
    "ASSMA","ASSAD","ARTES","ATL","ATB","AMS","AMI","AB","AL","AETEC","ADWYA",
]

#loop through all the links
for link in links:

    # Open the target webpage for each date range
    driver.get(LINK+link)


    start_date = datetime.strptime(START_DATE, "%d/%m/%Y").date()
    #add a 3 month period
    end_date = start_date + relativedelta(months= 3)

    while datetime.today().date() > end_date:    
        
        # Wait until the date pickers are available (adjust selectors as needed)
        wait = WebDriverWait(driver, 10)
        start_picker = wait.until(EC.element_to_be_clickable((By.ID, "dtFrom")))
        end_picker = wait.until(EC.element_to_be_clickable((By.ID, "dtTo")))
        
        # Clear any existing values and input the new dates
        start_picker.clear()
        start_picker.send_keys(start_date.strftime("%d/%m/%Y"))
        
        end_picker.clear()
        end_picker.send_keys(end_date.strftime("%d/%m/%Y"))
        
        # Optional pause to let the page update based on new dates
        time.sleep(1)
        
        # Locate and click the download button (adjust the selector as needed)
        download_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@class='btnR ml10']")))
        download_button.click()
        
        # Wait for the download to complete (adjust the duration as necessary)
        time.sleep(3)
        
        #update the start and end dates
        start_date = end_date
        end_date = start_date + relativedelta(months= 3)

# Close the browser after processing all date ranges
driver.quit()

