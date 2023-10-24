#mariadb -u root -p

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import *
from sqlalchemy import create_engine 
from azure.storage.blob.aio import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError
import pika
import os
import json

# http://raspinas.iptime.org:15672/ rabbitmq

BASE_DIR = os.path.dirname(os.path.abspath("secrets.json"))
SECRET_FILE = os.path.join(BASE_DIR, "secrets.json")
secrets = json.loads(open(SECRET_FILE).read())
DB = secrets["DB"]
DB_URL = f"mysql+pymysql://{DB['user']}:{DB['password']}@{DB['host']}:{DB['port']}/{DB['database']}?charset=utf8"
AZURE_CONNECTION_STRING = DB["azureConnectionString"]

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
    

class azureBlobStorage:
    async def exist(self, container: str, name: str):
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
        container_name = container
        async with blob_service_client:
            container_client = blob_service_client.get_container_client(container_name)
            try:
                blob_client = container_client.get_blob_client(name)
            except Exception as e:
                print("[AZURE Error - database.exist]",type(e),e)
                return False
            if(await blob_client.exists()):
                return 1
            else:
                return -1

    async def upload(self, container: str, file: bytes , name: str):
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
        container_name = container
        async with blob_service_client:
            container_client = blob_service_client.get_container_client(container_name)
            try:
                blob_client = container_client.get_blob_client(name)
                await blob_client.upload_blob(file)
            except Exception as e:
                print("[AZURE Error - database.upload]",type(e),e)
                return False
            
        return blob_client.url
    
    async def delete(self, container: str, name: str):
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
        container_name = container
        async with blob_service_client:
            container_client = blob_service_client.get_container_client(container_name)
            try:
                blob_client = container_client.get_blob_client(name)
                await blob_client.delete_blob()
            except ResourceNotFoundError:
                print("[AZURE Error - database.delete(1)]", ResourceNotFoundError, "The specified blob does not exist.")
                return -1
            except Exception as e:
                print("[AZURE Error - database.delete(2)]",type(e),e)
                return False
            return True

# class rabbitmq:
#     def __init__(self):
#         self.__url = DB['host']
#         self.__port = DB['rabbitmqPort']
#         self.__vhost = DB['rabbitmqVhost']
#         self.__cred = pika.PlainCredentials(DB['rabbitmqUser'], DB['password'])
#         return
    
#     async def setup(self, routing_key: str):
#         conn = pika.BlockingConnection(pika.ConnectionParameters(self.__url, self.__port, self.__vhost, self.__cred))
#         chan = conn.channel()
#         chan.exchange_declare(exchange='chat.exchange.'+routing_key, exchange_type='direct',durable=True)
#         chan.queue_declare(queue='chat.queue.'+routing_key)
#         chan.queue_bind(exchange='chat.exchange.'+routing_key,queue='chat.queue.'+routing_key, routing_key='chat.routing.'+routing_key)
#         return
    
#     async def setupBackup(self):
#         conn = pika.BlockingConnection(pika.ConnectionParameters(self.__url, self.__port, self.__vhost, self.__cred))
#         chan = conn.channel()
#         chan.exchange_declare(exchange='chatRecode.exchange', exchange_type='direct',durable=True)
#         chan.queue_declare(queue='chatRecode.queue')
#         chan.queue_bind(exchange='chatRecode.exchange',queue='chatRecode.queue', routing_key='chatRecode.routing')
#         return
    
#     async def create_chat(self, routing_key: str, body):
#         conn = pika.BlockingConnection(pika.ConnectionParameters(self.__url, self.__port, self.__vhost, self.__cred))
#         chan = conn.channel()
#         chan.basic_publish(
#             exchange = 'chat.exchange.'+routing_key,
#             routing_key = "chat.routing." + routing_key,
#             body = body
#         )
#         conn.close()
#         return
    

#     async def backup_chat(self, body):
#         conn = pika.BlockingConnection(pika.ConnectionParameters(self.__url, self.__port, self.__vhost, self.__cred))
#         chan = conn.channel()
#         chan.basic_publish(
#             exchange = 'chatRecode.exchange',
#             routing_key = "chatRecode.routing",
#             body = body
#         )
#         conn.close()
#         return
    

    
#     # def on_message(ch, method_frame, header_frame, body):
#     #     print('Received %s' % body)
    
#     #not use
#     async def get_chat(self, routing_key: str, callback: Function):
#         conn = pika.BlockingConnection(pika.ConnectionParameters(self.__url, self.__port, self.__vhost, self.__cred))
#         chan = conn.channel()
#         chan.basic_consume(
#             queue = "chat.queue."+routing_key,
#             #on_message_callback = rabbitmq.on_message,
#             on_message_callback = await callback,
#             auto_ack = True
#         )
#         print('Consumer is starting...')
#         chan.start_consuming()


#         # return chan.consume(
#         #     queue = "chat.queue."+routing_key,
#         #     auto_ack = True
#         # )



    
