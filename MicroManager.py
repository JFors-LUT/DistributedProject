##Jarno Forsblom Distributed systems final project
import socket
import threading
import pika
import uuid
import json

HOST = 'localhost'
PORT = 8000

class MicroManager:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', heartbeat=10, blocked_connection_timeout=10))
        self.channel = self.connection.channel()

        self.result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = self.result.method.queue

        self.channel.basic_consume(queue=self.callback_queue, on_message_callback=self.on_response, auto_ack=True)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body.decode()

    def sendRequest(self, url):
        self.response = None
        self.corr_id = str(uuid.uuid4())

        message = json.dumps({'url': url, 'corr_id': self.corr_id})

        self.channel.basic_publish(
                exchange='', 
                routing_key='crawler_queue', 
                properties=pika.BasicProperties(
                    reply_to=self.callback_queue, 
                    correlation_id=self.corr_id,), 
                    body=message)

        while self.response is None:
            self.connection.process_data_events()

        return json.loads(self.response)
    
    def processData(self, data, url):
        self.response = None
        self.corr_id = str(uuid.uuid4())

        message = json.dumps({'url': url, 'corr_id': self.corr_id, 'content': data})

        self.channel.basic_publish(
            exchange='',
            routing_key='data_queue',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,),
                body=message)
        
        while self.response is None:
            self.connection.process_data_events()
        
        return json.loads(self.response)
    
    def monitorHealth(self, data, url):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        message = json.dumps({'url': url, 'corr_id': self.corr_id, 'content': str(data)})
        self.channel.basic_publish(exchange='',
                          routing_key='health_queue',
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
            service = 'crawler'
            print("Crawling {}".format(message))
            response = micro_manager.sendRequest(message)
            if response['content'] == 0:
                conn.send("Connection error. Incorrect URL or requested website is down.".encode())
            else: 
                processBody = micro_manager.processData(response['content'], message)
                conn.send(processBody['content'].encode())
                healthCheck = micro_manager.monitorHealth(addr, message)

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