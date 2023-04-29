import pika
import json
import time
from datetime import datetime

class HealthMonitoring:
    def __init__(self):

        #crawlcount to show number of requests
        self.crawlcount = 0
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        
        #health_monitor_queue bound to health_check with routing key health_monitor
        self.channel.exchange_declare(exchange='health_check', exchange_type='direct')
        self.channel.queue_declare(queue='health_monitor_queue')
        #self.channel.queue_bind(queue='health_monitor_queue', exchange='health_check', routing_key='health_monitor')

        self.channel.basic_consume(queue='health_monitor_queue', on_message_callback=self.on_health_check)



    def on_health_check(self, ch, method, props, body):
        
        message = json.loads(body.decode())
        url = message['url']

        user = message['content']
        corr_id = message['corr_id']
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        
        #failed service returns 0, notify on console
        if url == 0:
             print(('[{}]: Crawl from user {} failed.'.format(current_time, user)))
        #else log succesful service
        else:
            self.crawlcount += 1
            healthCheck(current_time, user, url)
            response_message = json.dumps({'content': user, 'url': url})
            print('[{}]: {} crawl(s) succesfully executed.'.format(current_time, self.crawlcount))    
        #acknowledge to purge the message 
        ch.basic_ack(delivery_tag=method.delivery_tag)

#log user and crawls to file 
def healthCheck(current_time, user, url, ):
        file_write = json.dumps({'time': current_time, 'user': user, 'url':url})
        with open('user_crawl.txt', 'a') as file:
              file.write(file_write+'\n')
        file.close()

if __name__ == '__main__':
    monitor = HealthMonitoring()

    print('Health monitor is running...')
    monitor.channel.start_consuming()
