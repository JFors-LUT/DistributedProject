from bs4 import BeautifulSoup
import requests

def processData(URL, returnSite):

    soup = BeautifulSoup(returnSite.content, 'html.parser')

    if URL == 'iltalehti.fi':
        dataPacket = caseIltalehti(soup)
        return dataPacket
    else:
        dataPacket = soup.find('body')
        return dataPacket
    
def caseIltalehti(soup):
    text = "" 
    textList = []
    #titleClass = 

    for element in soup.find_all('div', class_='front-title a-title-font'):
        print(element.text.strip())
        text += element.text.strip()+'\n'
    return text
