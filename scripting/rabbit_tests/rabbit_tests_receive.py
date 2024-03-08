import pika, sys, os
import time

def main():
    # def function for receving message
    def any_name_for_callback(ch, method, properties, body):
        print(f" [x] received {body}")
        time.sleep(body.count(b'.'))
        print(" [x] Done")
    # create the connection and channel
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # create a queue for messages
    channel.queue_declare(queue='hello')

    # read ("consume") a message
    channel.basic_consume(queue='hello',
                          auto_ack=True,
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