#mariadb -u root -p

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import *
from sqlalchemy import create_engine 
import pika
import os
import json

# http://raspinas.iptime.org:15672/

BASE_DIR = os.path.dirname(os.path.abspath("secrets.json"))
SECRET_FILE = os.path.join(BASE_DIR, "secrets.json")
secrets = json.loads(open(SECRET_FILE).read())
DB = secrets["DB"]

DB_URL = f"mysql+pymysql://{DB['user']}:{DB['password']}@{DB['host']}:{DB['port']}/{DB['database']}?charset=utf8"

class engineconn:

    def __init__(self):
        self.engine = create_engine(DB_URL)

    def sessionmaker(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        return session

    def connection(self):
        conn = self.engine.connect()
        return conn
    

class rabbitmq:
    def __init__(self):
        self.__url = DB['host']
        self.__port = DB['rabbitmqPort']
        self.__vhost = DB['rabbitmqVhost']
        self.__cred = pika.PlainCredentials(DB['rabbitmqUser'], DB['password'])
        return
    
    async def setup(self, routing_key: str):
        conn = pika.BlockingConnection(pika.ConnectionParameters(self.__url, self.__port, self.__vhost, self.__cred))
        chan = conn.channel()
        chan.exchange_declare(exchange='chat.exchange.'+routing_key, exchange_type='direct',durable=True)
        chan.queue_declare(queue='chat.queue.'+routing_key)
        chan.queue_bind(exchange='chat.exchange.'+routing_key,queue='chat.queue.'+routing_key, routing_key='chat.routing.'+routing_key)
        return
    
    async def setupBackup(self):
        conn = pika.BlockingConnection(pika.ConnectionParameters(self.__url, self.__port, self.__vhost, self.__cred))
        chan = conn.channel()
        chan.exchange_declare(exchange='chatRecode.exchange', exchange_type='direct',durable=True)
        chan.queue_declare(queue='chatRecode.queue')
        chan.queue_bind(exchange='chatRecode.exchange',queue='chatRecode.queue', routing_key='chatRecode.routing')
        return
    
    async def create_chat(self, routing_key: str, body):
        conn = pika.BlockingConnection(pika.ConnectionParameters(self.__url, self.__port, self.__vhost, self.__cred))
        chan = conn.channel()
        chan.basic_publish(
            exchange = 'chat.exchange.'+routing_key,
            routing_key = "chat.routing." + routing_key,
            body = body
        )
        conn.close()
        return
    

    async def backup_chat(self, body):
        conn = pika.BlockingConnection(pika.ConnectionParameters(self.__url, self.__port, self.__vhost, self.__cred))
        chan = conn.channel()
        chan.basic_publish(
            exchange = 'chatRecode.exchange',
            routing_key = "chatRecode.routing",
            body = body
        )
        conn.close()
        return
    

    
    # def on_message(ch, method_frame, header_frame, body):
    #     print('Received %s' % body)
    
    #not use
    async def get_chat(self, routing_key: str, callback: Function):
        conn = pika.BlockingConnection(pika.ConnectionParameters(self.__url, self.__port, self.__vhost, self.__cred))
        chan = conn.channel()
        chan.basic_consume(
            queue = "chat.queue."+routing_key,
            #on_message_callback = rabbitmq.on_message,
            on_message_callback = await callback,
            auto_ack = True
        )
        print('Consumer is starting...')
        chan.start_consuming()


        # return chan.consume(
        #     queue = "chat.queue."+routing_key,
        #     auto_ack = True
        # )



    
