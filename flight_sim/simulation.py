from utils import generate_fligh_path, get_current_position, setup_logger, DELAY
from kafka_connector import KafkaConnector

import logging
import time
import json

logger = setup_logger('sim')

num_flights = 100
active_flights = []

kafka = KafkaConnector()

while True:
    while len(active_flights) < num_flights:
        active_flights.append(generate_fligh_path())
        # logger.info(f"Flight: {active_flights[-1]['flight_id']} Took off")
    time.sleep(DELAY)
    for i, flight in enumerate(active_flights):
        landed, curr_pos = get_current_position(flight)
        if landed:
            flight = active_flights.pop(i)
            # logger.info(f"Flight: {flight['flight_id']} Landed")
            flight['landed'] = True
        else:
            flight = active_flights[i]
            flight['curr'] = curr_pos
        kafka.send_message(json.dumps(flight))
        # print(json.dumps(flight))