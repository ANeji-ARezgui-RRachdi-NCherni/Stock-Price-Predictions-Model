from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Replace with the actual path to your msedgedriver executable
edgedriver_path = "C:/Users/rezgu/webdriver/msedgedriver.exe"

# Set up EdgeDriver
service = Service(executable_path=edgedriver_path)
driver = webdriver.Edge(service=service)
links=[
    "https://www.ilboursa.com/marches/download/HL",
    "https://www.ilboursa.com/marches/download/GIF",
    "https://www.ilboursa.com/marches/download/ECYCL",
    "https://www.ilboursa.com/marches/download/SOKNA",
    "https://www.ilboursa.com/marches/download/NAKL",
    "https://www.ilboursa.com/marches/download/LSTR",
    "https://www.ilboursa.com/marches/download/ELBEN",
    "https://www.ilboursa.com/marches/download/DH",
    "https://www.ilboursa.com/marches/download/CITY",
    "https://www.ilboursa.com/marches/download/SCB",
    "https://www.ilboursa.com/marches/download/CIL",
    "https://www.ilboursa.com/marches/download/CREAL",
    "https://www.ilboursa.com/marches/download/CELL",
    "https://www.ilboursa.com/marches/download/CC",
    "https://www.ilboursa.com/marches/download/BTE",
    "https://www.ilboursa.com/marches/download/BIAT",
    "https://www.ilboursa.com/marches/download/BHL",
    "https://www.ilboursa.com/marches/download/BH",
    "https://www.ilboursa.com/marches/download/BHASS",
    "https://www.ilboursa.com/marches/download/BL",
    "https://www.ilboursa.com/marches/download/BNA",
    "https://www.ilboursa.com/marches/download/BT",
    "https://www.ilboursa.com/marches/download/TJARI",
    "https://www.ilboursa.com/marches/download/TJL",
    "https://www.ilboursa.com/marches/download/AST",
    "https://www.ilboursa.com/marches/download/ASSMA",
    "https://www.ilboursa.com/marches/download/ASSAD",
    "https://www.ilboursa.com/marches/download/ARTES",
    "https://www.ilboursa.com/marches/download/ATL",
    "https://www.ilboursa.com/marches/download/ATB",
    "https://www.ilboursa.com/marches/download/AMS",
    "https://www.ilboursa.com/marches/download/AMI",
    "https://www.ilboursa.com/marches/download/AB",
    "https://www.ilboursa.com/marches/download/AL",
    "https://www.ilboursa.com/marches/download/AETEC",
    "https://www.ilboursa.com/marches/download/ADWYA",
]

# Define 3-month date ranges from 1st Jan 2010 to 4th Mar 2025 in dd/mm/yyyy format
date_ranges = [
    ("01/01/2010", "31/03/2010"),
    ("01/04/2010", "30/06/2010"),
    ("01/07/2010", "30/09/2010"),
    ("01/10/2010", "31/12/2010"),
    ("01/01/2011", "31/03/2011"),
    ("01/04/2011", "30/06/2011"),
    ("01/07/2011", "30/09/2011"),
    ("01/10/2011", "31/12/2011"),
    ("01/01/2012", "31/03/2012"),
    ("01/04/2012", "30/06/2012"),
    ("01/07/2012", "30/09/2012"),
    ("01/10/2012", "31/12/2012"),
    ("01/01/2013", "31/03/2013"),
    ("01/04/2013", "30/06/2013"),
    ("01/07/2013", "30/09/2013"),
    ("01/10/2013", "31/12/2013"),
    ("01/01/2014", "31/03/2014"),
    ("01/04/2014", "30/06/2014"),
    ("01/07/2014", "30/09/2014"),
    ("01/10/2014", "31/12/2014"),
    ("01/01/2015", "31/03/2015"),
    ("01/04/2015", "30/06/2015"),
    ("01/07/2015", "30/09/2015"),
    ("01/10/2015", "31/12/2015"),
    ("01/01/2016", "31/03/2016"),
    ("01/04/2016", "30/06/2016"),
    ("01/07/2016", "30/09/2016"),
    ("01/10/2016", "31/12/2016"),
    ("01/01/2017", "31/03/2017"),
    ("01/04/2017", "30/06/2017"),
    ("01/07/2017", "30/09/2017"),
    ("01/10/2017", "31/12/2017"),
    ("01/01/2018", "31/03/2018"),
    ("01/04/2018", "30/06/2018"),
    ("01/07/2018", "30/09/2018"),
    ("01/10/2018", "31/12/2018"),
    ("01/01/2019", "31/03/2019"),
    ("01/04/2019", "30/06/2019"),
    ("01/07/2019", "30/09/2019"),
    ("01/10/2019", "31/12/2019"),
    ("01/01/2020", "31/03/2020"),
    ("01/04/2020", "30/06/2020"),
    ("01/07/2020", "30/09/2020"),
    ("01/10/2020", "31/12/2020"),
    ("01/01/2021", "31/03/2021"),
    ("01/04/2021", "30/06/2021"),
    ("01/07/2021", "30/09/2021"),
    ("01/10/2021", "31/12/2021"),
    ("01/01/2022", "31/03/2022"),
    ("01/04/2022", "30/06/2022"),
    ("01/07/2022", "30/09/2022"),
    ("01/10/2022", "31/12/2022"),
    ("01/01/2023", "31/03/2023"),
    ("01/04/2023", "30/06/2023"),
    ("01/07/2023", "30/09/2023"),
    ("01/10/2023", "31/12/2023"),
    ("01/01/2024", "31/03/2024"),
    ("01/04/2024", "30/06/2024"),
    ("01/07/2024", "30/09/2024"),
    ("01/10/2024", "31/12/2024"),
    ("01/01/2025", "04/03/2025")
]
#loop through all the links
for link in links:

    # Open the target webpage for each date range
    driver.get(link)

    # Loop through each date range to perform the download
    for start_date, end_date in date_ranges:
        
        # Wait until the date pickers are available (adjust selectors as needed)
        wait = WebDriverWait(driver, 10)
        start_picker = wait.until(EC.element_to_be_clickable((By.ID, "dtFrom")))
        end_picker = wait.until(EC.element_to_be_clickable((By.ID, "dtTo")))
        
        # Clear any existing values and input the new dates
        start_picker.clear()
        start_picker.send_keys(start_date)
        
        end_picker.clear()
        end_picker.send_keys(end_date)
        
        # Optional pause to let the page update based on new dates
        time.sleep(1)
        
        # Locate and click the download button (adjust the selector as needed)
        download_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@class='btnR ml10']")))
        download_button.click()
        
        # Wait for the download to complete (adjust the duration as necessary)
        time.sleep(3)

# Close the browser after processing all date ranges
driver.quit()

