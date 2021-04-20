import pyodbc
import random
import re
import requests
import time
from bs4 import BeautifulSoup

# Connect to SQLServer database
conn = pyodbc.connect("Driver={SQL Server};Server=DESKTOP-U3ATH6F;Database=Final Year Project;"
                      "Trusted_Connection=yes;")

# User Agent List
HEADERS = ({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/86.0.4240.99 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,"
                      "*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "DNT": "1",
            "Connection": "close",
            "Upgrade-Insecure-Requests": "1",
            })

# Fetch the IDs
cursor = conn.cursor()
rows = cursor.execute("SELECT DISTINCT T1.[item_id] FROM [Final Year Project].[dbo].[Amazon_Video_Games_Ratings] T1 "
                      "LEFT JOIN [Final Year Project].[dbo].[Item_Id_To_Keywords] T2 ON T2.[item_id] = T1.[item_id] "
                      "WHERE T2.[item_id] IS NULL")

regex = re.compile('[^a-zA-Z0-9]')

# Iterate through each of the IDs
for amazon_id in list(rows):

    # Strip non-alphanumeric characters from amazon_id, as originally contains brackets and commas
    stripped_amazon_id = regex.sub('', str(amazon_id))

    # Access the relevant Amazon page
    amazon_url = "https://www.amazon.co.uk/s?k=" + stripped_amazon_id
    print(amazon_url)
    amazon_page = requests.get(amazon_url, headers=HEADERS)

    # Create the object that will contain all the info in the URL
    soup = BeautifulSoup(amazon_page.content, features="lxml")

    # Product title without HTML tags or whitespace
    title = soup.find("span", {"class": "a-size-medium a-color-base a-text-normal"})
    if title is not None:
        escaped_title = title.get_text().strip().replace("'", "")
    else:
        escaped_title = ""
    print("Amazon Product Name:", escaped_title)

    sql_text = "INSERT INTO [Final Year Project].[dbo].[Item_Id_To_Keywords](item_id, keywords) VALUES('{0}','{1}');" \
        .format(stripped_amazon_id, escaped_title)

    try:
        cursor.execute(sql_text)
        cursor.commit()
    except pyodbc.IntegrityError as error:
        print(error)

    time.sleep(random.randint(5, 12))

cursor.close()
conn.close()
