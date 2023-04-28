import pika
import json
import time
from datetime import datetime

class HealthMonitoring:
    def __init__(self):

        self.crawlcount = 0
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()

        
        self.channel.queue_declare(queue='health_queue')
        self.channel.basic_consume(queue='health_queue', on_message_callback=self.on_request)


    def on_request(self, ch, method, props, body):
        message = json.loads(body.decode())
        url = message['url']
        user = message['content']
        corr_id = message['corr_id']

        self.crawlcount += 1
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        healthCheck(user, url)
        print('[{}]: {} crawl(s) succesfully executed.'.format(current_time, self.crawlcount))

#log user made crawls to file 
def healthCheck(user, url):
        file_write = json.dumps({'user': user, 'url':url})
        with open('user_crawl.txt', 'a') as file:
              file.write(file_write+'\n')
        file.close()



if __name__ == '__main__':
    monitor = HealthMonitoring()

    print('Health monitor is running...')
    monitor.channel.start_consuming()
