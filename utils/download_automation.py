from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
import argparse
import os
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromiumService


load_dotenv()
#constants
LINK =  "https://www.ilboursa.com/marches/download/"
# START_DATE = "01/01/2010"

def get_dates(start):
    """
    Converts start date from string format to date object
    If start date is equal to current date ,it returns todays date value in start_date and end_date
    input:
        start: start date in string format "dd/mm/yyyy"
    Returns:
        start_date: start date as date object
        end_date: date after 89 days period as date object

    """
    today=datetime.today().date()
    if datetime.strptime(start, "%d/%m/%Y").date() == today:
        start_date= end_date= today
    else:
        start_date = datetime.strptime(start, "%d/%m/%Y").date()
        end_date = start_date + relativedelta(days= 89)
    
    return start_date, end_date

def update_dates(date):
    """
    Updates the date range 
    input:
        date: date object
    Returns:
        start_date: next day date from input as date object
        end_date: date after start_date with 89 days period as date object

    """
    start_date= date + relativedelta(days= 1)
    end_date=start_date+relativedelta(days= 89)
    return start_date,end_date

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

    chrome_options = Options()
    options = [
    "--headless=new",
    "--disable-gpu",
    "--window-size=1920,1200",
    "--ignore-certificate-errors",
    "--disable-extensions",
    "--no-sandbox",
    "--no-first-run",
    "--disable-dev-shm-usage"
]
    for option in options:
        chrome_options.add_argument(option)
    
    download_dir = os.path.join(os.getcwd(), "data")
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True
    })

    # Set up Driver
    service=ChromiumService(ChromeDriverManager(driver_version="134.0.6998.0", chrome_type=ChromeType.CHROMIUM).install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
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
    parser = argparse.ArgumentParser(description="Download automation for stock data.")
    parser.add_argument("--date", required=True, help="Start date in dd/mm/YYYY format")
    args = parser.parse_args()
    main(args.date)

