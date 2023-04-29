import socket
import sys


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

#connects to micormanager servic
def getWebsite(s):

    s.send("connect".encode())
    response = s.recv(1024).decode()
    print(response)
    
    sendURL(s)
    return 

def sendURL(s):
    #while loop to send URLs for processing, exit to kill the connection
    while True:
        try:
            message = input("URL: ")
            print("Connecting to service.... ")
            #exit to kill the connection
            if message == "exit":
                s.send("{}".format(message).encode())
                return 0
            elif message.strip() != "":
                s.send("{}".format(message).encode())
                #set to replace invalid unicode characters that would halt the program
                response = s.recv(4096).decode('utf-8', 'replace')
                print(response, end='')
                #if response larger than buffersize we fetch responses until buffer is empty
                while sys.getsizeof((response)) > 4096:
                    response = s.recv(4096).decode('utf-8', 'replace')
                    print(response, end='')
                print('')
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

if __name__ == "__main__":
    clientRun() #rabbitmq-server start <--- command note to run rabbitMQ server
                