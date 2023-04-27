##Jarno Forsblom Distributed systems final project
#import Fetcher
import DataManager
import socket
import threading
import pika
import uuid
import json

HOST = 'localhost'
PORT = 8000
'''
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

def fetch_url(url):
    channel.queue_declare(queue='fetcher_queue')
    channel.basic_publish(exchange='', routing_key='fetcher_queue', body=url)
    print(" [x] Sent %r" % url)

    result_queue = channel.queue_declare(queue='result_queue')
    channel.basic_consume(queue='result_queue', on_message_callback=crawlback, auto_ack=True)
    return result_queue

def crawlback (ch, method, properties, body):
    title = body.decode()
    print("Received message:", title)
    #return title
'''
class MicroManager:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()

        self.result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = self.result.method.queue

        self.channel.basic_consume(queue=self.callback_queue, on_message_callback=self.on_response, auto_ack=True)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body.decode()

    def send_request(self, url):
        self.response = None
        self.corr_id = str(uuid.uuid4())

        message = json.dumps({'url': url, 'corr_id': self.corr_id})

        self.channel.basic_publish(exchange='', routing_key='crawler_queue', properties=pika.BasicProperties(reply_to=self.callback_queue, correlation_id=self.corr_id,), body=message)

        while self.response is None:
            self.connection.process_data_events()

        return json.loads(self.response)

def handleClient(conn, addr):
    print("New connection from {}".format(addr))
    micro_manager = MicroManager()
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
            print("Crawling {}".format(message))
            response = micro_manager.send_request(message)
            print(response['title'])
            if response == 0:
                conn.send("Connection error. Incorrect URL or requested website is down.".encode())
            else: 
                #processBody = DataManager.processData(message, returnBody)
                conn.send(response['title'].encode())
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