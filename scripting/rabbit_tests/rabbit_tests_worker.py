import pika, sys, os
import time

def main():
    # def function for receving message
    def any_name_for_callback(ch, method, properties, body):
        print(f" [x] received {body}")
        time.sleep(body.count(b'.'))
        print(" [x] Done")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    # create the connection and channel
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # create a queue for messages
    # channel.queue_declare(queue='hello')  # durable ensures queue survives RabbitMQ restart
    channel.queue_declare(queue='durable_queue', durable=True)  # durable ensures queue survives RabbitMQ restart
    #however for truly reliable queues and messages, check https://www.rabbitmq.com/confirms.html

    # read ("consume") a message
    channel.basic_consume(queue='hello',
                          # auto_ack=True, # turns off manual message acknowledgement
                          on_message_callback=any_name_for_callback)
    # keep consuming
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)