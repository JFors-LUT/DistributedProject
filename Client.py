import socket
import requests
from bs4 import BeautifulSoup

def menu():
    print("1) Connect to service\n0) Close connection\n")
    options = input("Enter your choice: ")
    return options

#test variable for easy access to localhost
def setServer(test):
    if test == 1:
        address = "localhost"
        return address
    
    address = input("Set server address: ")
    return address

def setPort(test):
    if test == 1:
        port = "8000"
        return port
    
    port = input("Set server port: ")
    return port

def getWebsite(s):

    s.send("connect".encode())
    response = s.recv(1024).decode()
    print(response)
    #check response and return to menu if channel or nickname invalid
    if response[:5] == "Sorry":
        return 1
    
    sendURL(s)
    return 

def sendURL(s):

    while True:
        try:
            message = input("URL: ")

            #start messages with exit to kill the connection or /w for private message  
            if message == "exit":
                s.send("{}".format(message).encode())
                return 0
            elif message.strip() != "":
                s.send("{}".format(message).encode())
                response = s.recv(8192).decode('utf-8')
                print(response)
        except ConnectionResetError:
            return 0


def clientRun():
    test = 1 #set 1 for localhost:8000
    host = setServer(test)
    port = setPort(test)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            print("Connecting to the server...\n")
            s.connect((host, int(port)))
            failed = False
        except ConnectionRefusedError:
            print("Failed connection to server {}:{}".format(host, port))
            failed = True

        while True:
            if failed == True:
                break
            else:
                getWebsite(s)
                s.shutdown(2)
                break

def crawl():
    #while True:
        #url = input("URL: ")
        url = 'https://www.google.com.com'
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            links = soup.find_all('a')
            for link in links:
                print(link.get('href'))

            
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            for p in soup.find_all('h1'):
                print(p.text)
        except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
            print("We ran into a problem. Please check your URL is correct.")
    
        return links




if __name__ == "__main__":
    clientRun()
    #print(crawl())
                