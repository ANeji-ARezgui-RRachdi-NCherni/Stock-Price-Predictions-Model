from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
import os
from dotenv import load_dotenv


load_dotenv()
#constants
LINK =  "https://www.ilboursa.com/marches/download/"
# START_DATE = "01/01/2010"

def get_dates(start):
    today=datetime.today().date()
    if datetime.strptime(start, "%d/%m/%Y").date() == today:
        start_date= end_date= today
    else:
        start_date = datetime.strptime(start, "%d/%m/%Y").date()
        end_date = start_date + relativedelta(days= 89)
    
    return start_date, end_date

def update_dates(end):
    start=end + relativedelta(days= 1)
    end=start+relativedelta(days= 89)
    return start,end

def download_data(start_date, end_date ,driver):
    
    # Wait until the date pickers are available (adjust selectors as needed)
    wait = WebDriverWait(driver, 10)
    start_picker = wait.until(EC.element_to_be_clickable((By.ID, "dtFrom")))
    end_picker = wait.until(EC.element_to_be_clickable((By.ID, "dtTo")))
    
    # Clear any existing values and input the new dates
    start_picker.clear()
    start_picker.send_keys(start_date.strftime("%d/%m/%Y"))
    
    end_picker.clear()
    end_picker.send_keys(end_date.strftime("%d/%m/%Y"))
    
    # pause to let the page update based on new dates
    time.sleep(1)
    
    # Locate and click the download button (adjust the selector as needed)
    download_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@class='btnR ml10']")))
    download_button.click()
    
    # Wait for the download to complete (adjust the duration as necessary)
    time.sleep(3)
            
            
            
def main(date):
    # browser webdriver
    edgedriver_path =os.getenv('WEB_DRIVER_PATH')

    # Set up EdgeDriver
    service = Service(executable_path=edgedriver_path)
    driver = webdriver.Edge(service=service)

    # Stock Symbols
    links= [ "HL","GIF","ECYCL","SOKNA","NAKL","LSTR","ELBEN","DH","CITY","SCB","CIL","CREAL",
    "CELL","CC","BTE","BIAT","BHL","BH","BHASS","BL","BNA","BT","TJARI","TJL","AST",
    "ASSMA","ASSAD","ARTES","ATL","ATB","AMS","AMI","AB","AL","AETEC","ADWYA"] 

    today=datetime.today().date()

    for link in links:

        start_date, end_date= get_dates(date)
        driver.get(LINK+link)

        while  today >= start_date: 
            download_data(start_date,end_date,driver)
            #update the start and end dates
            start_date, end_date = update_dates(end_date)
    # Close the browser after processing all the links
    driver.quit()


if __name__ =="__main__":
    date=input("enter start date")
    main(date) 

