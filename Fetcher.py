import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
'''
def getContent(message):
        print(message)
        try:
            if message[:4] == "http":
                response = requests.get(message)
            else:
                response = requests.get('https://www.', message)
            soup = BeautifulSoup(response.content, 'html.parser')
            body_text = soup.find('body')
            return body_text
        except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
            print("failed")
            return 0
'''

def getContent(message):
    try:
        session = requests.Session()
        retry = Retry(connect=2, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        if message[:4] == "http":
            response = requests.get(message)
            #soup = BeautifulSoup(response.content, 'html.parser')
            return response

        else:
            message = 'https://'+message
            response = session.get(message)
            #soup = BeautifulSoup(response.content, 'html.parser')
            #body_text = soup.find('body')
            return response
            #return response
    except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
        print("failed")
        return 0

