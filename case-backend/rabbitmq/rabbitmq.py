import json
import logging
import threading
import time

from django.conf import settings
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection
from pika.connection import URLParameters
from pika.exceptions import AMQPConnectionError, ConnectionClosed, StreamLostError
from pika.exchange_type import ExchangeType
from pika.spec import Basic, BasicProperties


class RabbitMQ:
    __isInstantiated = False
    
    @staticmethod
    def __init__():
        if RabbitMQ.__isInstantiated:
            raise Exception("RabbitMQ is already instantiated")
        RabbitMQ.queue()
        RabbitMQ.__isInstantiated = True

    @staticmethod
    def queue(message):
        try:
            parameters = URLParameters(settings.AMQP_URI)
            RabbitMQ.__connection = BlockingConnection(parameters)
            RabbitMQ.__channel = RabbitMQ.__connection.channel()
            RabbitMQ.__channel.queue_declare(queue="discord_queue")
            RabbitMQ.__channel.basic_publish(
                    exchange="",
                    routing_key="discord_queue",
                    body=message,
                    properties=BasicProperties(content_type="application/json"),
                )
            RabbitMQ.__channel.close()
            

        except (StreamLostError, AMQPConnectionError):
            raise Exception("service RabbitMQ: cannot connect to rabbitmq")
        
    @staticmethod
    def isInstantiated():
        return RabbitMQ.__isInstantiated