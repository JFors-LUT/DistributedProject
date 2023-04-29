##Jarno Forsblom Distributed systems final project
import socket
import threading
import pika
import uuid
import json
import time

HOST = 'localhost'
PORT = 8000

class MicroManager:
    def __init__(self):
        #variable to manage wait time on response and inform client
        self.retry_connection = 10
        #create pika connection as localhost
        
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()

        #creates queue to receive responses from other microservices
        self.result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = self.result.method.queue

        self.channel.basic_consume(queue=self.callback_queue, on_message_callback=self.on_response, auto_ack=True)

    #check if response properties correspond to correlation id
    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body.decode()

    #send pagecrawl request to Crawler.py
    def sendRequest(self, url):
        retries = self.retry_connection
        self.response = None
        self.corr_id = str(uuid.uuid4())

        #Use json for API
        message = json.dumps({'url': url, 'corr_id': self.corr_id})

        #publish message to crawler_queue with variables for return message
        self.channel.basic_publish(
                exchange='', 
                routing_key='crawler_queue', 
                properties=pika.BasicProperties(
                    reply_to=self.callback_queue, 
                    correlation_id=self.corr_id,), 
                    body=message)
        
        #wait for response and move on after self.retry_connection tries if service not responding 
        while self.response is None:
            retries -= 1
            self.connection.process_data_events()
            time.sleep(1)
            if retries == 0:
                return {'content': retries}

        return json.loads(self.response)
    
    #send message to DataManager.py
    def processData(self, data, url):
        retries = self.retry_connection
        self.response = None
        self.corr_id = str(uuid.uuid4())
        message = json.dumps({'url': url, 'corr_id': self.corr_id, 'content': data})

        #send to data_queue and get response
        self.channel.basic_publish(
            exchange='',
            routing_key='data_queue',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,),
                body=message)
        
        #wait for response and move on after tries
        while self.response is None:
            retries -= 1
            self.connection.process_data_events()
            time.sleep(1)
            if retries == 0:
                return {'content': retries}
        return json.loads(self.response)
    
    def monitorHealth(self, data, url):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        message = json.dumps({'url': url, 'corr_id': self.corr_id, 'content': str(data)})

        self.channel.basic_publish(exchange='health_check', 
                                   routing_key='health_monitor', 
                                   body=message)
         
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
        message = data.decode()
        

        if message == 'exit':
            break
        elif message == 'connect':
            conn.send("Connection eshtablished. Please enter your URL (e.g. 'example.com' or 'exit' to close connection)".encode())
        else:
            print("Crawling {}".format(message))
            response = micro_manager.sendRequest(message)
            if response['content'] == 0:
                conn.send("Connection error. Incorrect URL or requested service is down.".encode())
                micro_manager.monitorHealth(addr, response['content'])
            else:
                response = micro_manager.processData(response['content'], message)
                if response['content'] == 0: 
                    conn.send("Connection error. Incorrect URL or requested service is down.".encode())
                    micro_manager.monitorHealth(addr, response['content'])
                else:
                    conn.send(response['content'].encode())

                micro_manager.monitorHealth(addr, message)

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