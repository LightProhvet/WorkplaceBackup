import pika
import logging

_logger = logging.getLogger(__name__)

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='test_topic', exchange_type='topic')
channel.queue_declare(queue="changes_queue")

channel.queue_bind(
        exchange='topic_logs', queue="changes_queue", routing_key="*.modified.*")


def callback_on_request(ch, method, props, body):
    _logger.info(f"\n\nserver received: \n {body}")
    response = "GOOD"

    ch.basic_publish(
        exchange='',
        routing_key=props.reply_to,
        properties=pika.BasicProperties(
            correlation_id=props.correlation_id
        ),
        body=str(response)
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='changes_queue', on_message_callback=callback_on_request)

_logger.info(f"  [x] Awaiting RPC requests")
channel.start_consuming()
