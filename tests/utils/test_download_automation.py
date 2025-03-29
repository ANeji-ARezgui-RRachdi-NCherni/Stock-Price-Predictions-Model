import pytest
from datetime import datetime
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from utils import get_dates, update_dates, download_data


@pytest.fixture
def date():
    return datetime.strptime("01/02/2013", "%d/%m/%Y").date()  

@pytest.fixture
def dates():
    start=datetime.strptime("01/02/2013", "%d/%m/%Y").date()
    end=datetime.strptime("01/03/2013", "%d/%m/%Y").date()
    return  start, end 

@pytest.fixture
def link():
    return "https://www.ilboursa.com/marches/download/HL"

@pytest.fixture
def driver():
    edgedriver_path =os.getenv('WEB_DRIVER_PATH')
    service = Service(executable_path=edgedriver_path)
    drv = webdriver.Edge(service=service)
    return drv

@pytest.fixture
def new_file():
    
    download_folder = "C:/Users/rezgu/Downloads"
    initial_files = set(os.listdir(download_folder))
    current_files = set(os.listdir(download_folder))
    return current_files - initial_files

def test_update_dates_raises():
   with pytest.raises(TypeError):
       update_dates("01/02/2013")

def test_update_dates(date):
    start_date,end_date=update_dates(date)
    assert start_date == date + relativedelta(days=1)
    assert end_date == date + relativedelta(days=90)         

def test_get_dates_raises(date):
    with pytest.raises(TypeError):
       get_dates(date)



def test_get_dates(date):
    start_date,end_date=get_dates("01/02/2013")
    assert start_date == date
    assert end_date == date + relativedelta(days=89)    


def test_download_data(dates,driver,link):
    driver.get(link)
    download_data(dates[0],dates[1],driver)
    assert new_file

