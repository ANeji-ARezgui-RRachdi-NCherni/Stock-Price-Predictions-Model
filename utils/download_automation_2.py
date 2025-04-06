import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

# Step 0: Create a session to manage cookies automatically
session = requests.Session()

# Step 1: First GET request to load page and retrieve token + cookies
url_get = "https://www.ilboursa.com/marches/download/PX1"
response_get = session.get(url_get)

# Step 2: Parse the __RequestVerificationToken from the HTML
soup = BeautifulSoup(response_get.text, "html.parser")
token_input = soup.find('input', {'name': '__RequestVerificationToken'})
if token_input is None:
    raise Exception("Token not found on page. Maybe the page structure changed?")
token = token_input['value']

# Step 3: Extract cookies explicitly
cookies = session.cookies.get_dict()

# Step 4: Prepare POST data (form fields)
data = {
    'dtFrom': '2025-04-01',
    '__Invariant': 'dtFrom',
    'dtTo': '2025-04-05',
    '__Invariant': 'dtTo',
    '__RequestVerificationToken': token
}

# Step 5: Prepare headers to mimic a real browser
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://www.ilboursa.com",
    "Referer": "https://www.ilboursa.com/marches/download/PX1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
}

# Step 6: Make POST request with data + headers + EXPLICIT cookies
response_post = session.post(url_get, data=data, headers=headers, cookies=cookies)

# Step 7: Save the downloaded file
if response_post.status_code == 200:
    if not os.path.exists("data/raw"):
        os.makedirs("data/raw")
    with open('data/raw/PX1.csv', 'wb') as f:
        f.write(response_post.content)
    print("✅ File downloaded and saved successfully as 'PX1.csv'")
else:
    print(f"❌ Failed to download file. Status code: {response_post.status_code}")

# Step 8 : check if the file is correct
df = pd.read_csv('data/raw/PX1.csv')
print(df.head())

