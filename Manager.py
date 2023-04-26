##Jarno Forsblom Distributed systems final project
import Fetcher
import socket
import threading

HOST = 'localhost'
PORT = 8000


def handleClient(conn, addr):
    print("New connection from {}".format(addr))
    while True:
        try:
            data = conn.recv(1024)
        except ConnectionResetError:
            print("Lost connection to {}".format(conn))
            break
        #break handshake if no data(shutdown)
        if not data:
            break
        
        #TODO connections and requests monitoring
        message = data.decode()
        

        if message == 'exit':
            break
        elif message == 'connect':
            conn.send("Connection eshtablished. Please enter your URL (e.g. 'example.com' or 'exit' to close connection)".encode())
        else:
            print("Crafling {}".format(message))
            returnBody = Fetcher.getContent(message)
            if returnBody == 0:
                conn.send("Connection error. Incorrect URL or requested website is down.".encode())
            else: 
                #TODO Data manager
                conn.send(returnBody.encode())
        print("Received message from {}: {}".format(addr, message))
    conn.close()
        

def serverStart():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print("Server listening on {}:{}".format(HOST, PORT))
        while True:
            conn, addr = s.accept()
            # create new thread for client
            t = threading.Thread(target=handleClient, args=(conn, addr))
            t.start()

if __name__ == '__main__':
    serverStart()