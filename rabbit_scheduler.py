import json
import pika

from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

conn_params = {
    'host_mq': os.environ.get('RABBITMQ_HOST'),
    'port_mq': os.environ.get('RABBITMQ_PORT'),
    'user_mq': os.environ.get('RABBITMQ_USER'),
    'password_mq': os.environ.get('RABBITMQ_PASSWORD'),
    'input_queue': os.environ.get('RABBITMQ_TASK_QUEUE')
}


class RabbitMQScheduler:
    def __init__(self):
        self.host_mq = os.environ.get('RABBITMQ_HOST')
        self.port_mq = int(os.environ.get('RABBITMQ_PORT'))
        self.user_mq = os.environ.get('RABBITMQ_USER')
        self.password_mq = os.environ.get('RABBITMQ_PASSWORD')
        self.task_queue = os.environ.get('RABBITMQ_TASK_QUEUE')

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.host_mq, port=self.port_mq, credentials=pika.PlainCredentials(self.user_mq, self.password_mq))
        )

        # # versions without credentials
        # self.connection = pika.BlockingConnection(
        #     pika.ConnectionParameters(
        #         host=self.host_mq, port=self.port_mq)
        # )


        self.channel = self.connection.channel()
        self.channel.queue_declare(self.task_queue)

    # queue_output - название очереди (string), task = задача в формате dictionary
    def send_task(self, task):
        self.channel.basic_publish(
            exchange = '', routing_key=self.task_queue, body=json.dumps(task))
        

array =  [
    {'handle' : "dimasidorenko", 'problem_id' : 32, 'sub_time': 50, 'verdict' : 'OK', "problem_rating" : 500 }, 
    {'handle' : "Skeef79", 'problem_id' : 57, 'sub_time': 50, 'verdict' : 'OK', "problem_rating" : 500 }]


sample_task = {
    'assignment_id' : 10, 
    'submissions' : array,
}

scheduler = RabbitMQScheduler()
scheduler.send_task(sample_task)