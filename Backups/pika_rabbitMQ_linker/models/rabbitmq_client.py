# -*- coding: utf-8 -*-

from itertools import chain
from odoo import api, fields, models, tools, _
import pika
import uuid
import logging

_logger = logging.getLogger(__name__)

class TestRpcClient(object):

    def __init__(self):
        self.connection = pika.BlockingConnection(parameters=pika.ConnectionParameters())
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='test_topic', exchange_type='topic')

        result = self.channel.queue_declare(queue='pricelist_change_confirmation', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True
        )

        self.response = None
        self.corr_id = None

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            _logger.info(f"\n\n I have received: {body}")
            self.response = body
            # ch.basic_ack(delivery_tag=method.delivery_tag)

    def call(self, input1, deleted_data=None, created_data=None):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='test_topic',
                      routing_key='test.modified.data',
                      body=str(input1),
                      properties=pika.BasicProperties(
                          reply_to=self.callback_queue,
                          delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE,
                          # content_type='application/json'  # the message format
                          correlation_id=self.corr_id,  # Useful to correlate RPC responses with requests.
                      ))
        if deleted_data:
            self.channel.basic_publish(exchange='test_topic',
                                       routing_key='test.deleted.data',
                                       body=str(deleted_data),
                                       properties=pika.BasicProperties(
                                           reply_to=self.callback_queue,
                                           delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE,
                                           # content_type='application/json'  # the message format
                                           correlation_id=self.corr_id,
                                           # Useful to correlate RPC responses with requests.
                                       ))
        if created_data:
            self.channel.basic_publish(exchange='test_topic',
                                       routing_key='test.created.data',
                                       body=str(created_data),
                                       properties=pika.BasicProperties(
                                           reply_to=self.callback_queue,
                                           delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE,
                                           # content_type='application/json'  # the message format
                                           correlation_id=self.corr_id,
                                           # Useful to correlate RPC responses with requests.
                                       ))
        self.connection.process_data_events(time_limit=None)

        return int(self.response)


class PricelistItem(models.Model):
    _name = 'rabbit.pika.client'

