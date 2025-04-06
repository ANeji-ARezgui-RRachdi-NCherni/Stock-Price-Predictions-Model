from datetime import datetime
from dateutil.relativedelta import relativedelta
import argparse
import requests
from bs4 import BeautifulSoup
import os

#constants
BASELINK =  "https://www.ilboursa.com/marches/download/"
EXPECTED_HEADERS = "symbole;date;ouverture;haut;bas;cloture;volume"

def get_dates(start):
    """
    Converts start date from string format to date object
    If start date is equal to current date ,it returns todays date value in start_date and end_date
    input:
        start: start date in string format "dd-mm-yyyy"
    Returns:
        start_date: start date as date object
        end_date: date after 28*3-1 = 83 days period as date object (taking into consideration feb = 28 days)

    """
    today=datetime.today().date()
    if datetime.strptime(start, "%d-%m-%Y").date() == today:
        start_date= end_date= today
    else:
        start_date = datetime.strptime(start, "%d-%m-%Y").date()
        end_date = start_date + relativedelta(days= 83)
    
    return start_date, end_date

def update_dates(date):
    """
    Updates the date range 
    input:
        date: date object
    Returns:
        start_date: next day date from input as date object
        end_date: date after start_date with 83 days period as date object

    """
    start_date= date + relativedelta(days= 1)
    end_date=start_date+relativedelta(days= 83)
    return start_date,end_date

def download_data(start_date, end_date ,cookies, token, session, link, fileName):
    # Extract cookies explicitly
    cookies = session.cookies.get_dict()

    # Prepare POST data (form fields)
    data = {
        'dtFrom': start_date,
        '__Invariant': 'dtFrom',
        'dtTo': end_date,
        '__Invariant': 'dtTo',
        '__RequestVerificationToken': token
    }

    # Prepare headers to mimic a real browser
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://www.ilboursa.com",
        "Referer": link,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    }

    # Make POST request with data + headers + EXPLICIT cookies
    response_post = session.post(link, data=data, headers=headers, cookies=cookies)

    file_path = f"data/raw/{fileName}"
    if response_post.status_code == 200:
        if not os.path.exists("data/raw"):
            os.makedirs("data/raw")
        response_post_content_to_array = response_post.content.decode().split('\r\n')
        if response_post_content_to_array[0] == EXPECTED_HEADERS: ## Ugly hack to check if the content is indeed a csv file (if there are no data the api call returns an html file)
            with open(file_path, 'a') as f:
                if os.stat(file_path).st_size == 0:
                    print(f"{file_path} created successfully")
                    f.write(f'{EXPECTED_HEADERS}\n')
                for i in range(1,len(response_post_content_to_array)): ## We skip first line because it's the headers
                    line = response_post_content_to_array[i]
                    if line != '':
                        f.write(f'{response_post_content_to_array[i]}\n')
    else:
        raise Exception(f"❌ Failed to download file. Status code: {response_post.status_code}")
            
def main(date):
    # Stock Symbols
    links= [ "HL","GIF","ECYCL","SOKNA","NAKL","LSTR","ELBEN","DH","CITY","SCB","CIL","CREAL",
    "CELL","CC","BTE","BIAT","BHL","BH","BHASS","BL","BNA","BT","TJARI","TJL","AST",
    "ASSMA","ASSAD","ARTES","ATL","ATB","AMS","AMI","AB","AL","AETEC","ADWYA"] 

    today=datetime.today().date()

    for link in links:

        start_date, end_date= get_dates(date)

        # Create a session to manage cookies automatically
        session = requests.Session()

        # First GET request to load page and retrieve token + cookies
        url_get = f'{BASELINK}{link}'
        response_get = session.get(url_get)

        # Parse the __RequestVerificationToken from the HTML
        soup = BeautifulSoup(response_get.text, "html.parser")
        token_input = soup.find('input', {'name': '__RequestVerificationToken'})
        if token_input is None:
            raise Exception("Token not found on page. Maybe the page structure changed?")
        token = token_input['value']

        cookies = session.cookies.get_dict()

        fileName = f'{link}.csv'

        while  today >= start_date:
            download_data(start_date,end_date,cookies,token,session,url_get,fileName)
            #update the start and end dates
            start_date, end_date = update_dates(end_date)

if __name__ =="__main__":
    parser = argparse.ArgumentParser(description="Download automation for stock data.")
    parser.add_argument("--date", required=True, help="Start date in dd-mm-YYYY format")
    args = parser.parse_args()
    main(args.date)

