from pykafka import KafkaClient
from pykafka.exceptions import NoBrokersAvailableError, SocketDisconnectedError

from utils import setup_logger

import time

logger = setup_logger('sim')

class KafkaConnector:
    def __init__(self, topic, hosts="127.0.0.1:9092,kafka:9092", retries=5):
        self.retries = retries
        self.topic = self.connect(hosts, topic)

    def connect(self, hosts, topic):
        tries = 0
        while True:
            try:
                tries += 1
                client = KafkaClient(hosts=hosts)
                logger.info("Connection success")
                topic = client.topics[topic]
                return topic
            except NoBrokersAvailableError:
                if tries == self.retries:
                    logger.error("No brokers found to connect.")
                    return None
                else:
                    logger.warning("Connection failed. Retrying...")
                    time.sleep(5)
    
    def send_message(self, message):
        if self.topic:
            tries = 0
            while tries < self.retries:
                try:
                    with self.topic.get_sync_producer() as producer:
                        producer.produce(message.encode())
                        return  # Exit the function after successful send
                except SocketDisconnectedError:
                    tries += 1
                    logger.warning(f"SocketDisconnectedError on send attempt {tries}. Retrying in 5 seconds...")
                    time.sleep(5)
                except Exception as e:
                    logger.error(f"Unexpected error while sending message: {e}")
                    break
            logger.error("Failed to send message after retries.")
        else:
            logger.error("No topic to send message.")

if __name__ == "__main__":
    kafka_connection = KafkaConnector('hello')
    kafka_connection.send_message("Hi")