import pika
import sys
import uuid

class FibonacciRpcClient(object):

    def __init__(self):
        self.connection = pika.BlockingConnection(parameters=pika.ConnectionParameters())
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            # auto_ack=True
        )

        self.response = None
        self.corr_id = None

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, n):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',
                      routing_key='rpc_queue',
                      body=str(n),
                      properties=pika.BasicProperties(
                          reply_to=self.callback_queue,
                          delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE,  # should be equal to 2
                          # content_type='application/json'  # the message format
                          correlation_id=self.corr_id,  # Useful to correlate RPC responses with requests.
                      ))
        self.connection.process_data_events(time_limit=None)
        return int(self.response)


fibonacci_rpc = FibonacciRpcClient()
input = ' '.join(sys.argv[1:]) or 30
print(f" [x] Requesting fib({input})")
response = fibonacci_rpc.call(int(input))
print(f" [.] Got {response}")
