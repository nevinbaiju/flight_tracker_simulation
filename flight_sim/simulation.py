from utils import generate_fligh_path, get_current_position, setup_logger
import logging
import time

logger = setup_logger('sim')

num_flights = 10000
active_flights = []

total_flights = 0
while True:
    while len(active_flights) < num_flights:
        active_flights.append(generate_fligh_path())
        logger.info(f"Flight: {active_flights[-1]['flight_id']} Took off")
        total_flights += 1
    time.sleep(5)
    for i, flight in enumerate(active_flights):
        landed, curr_pos = get_current_position(flight)
        if landed:
            landed_flight = active_flights.pop(i)
            logger.info(f"Flight: {landed_flight['flight_id']} Landed")
        else:
            active_flights[i]['curr'] = curr_pos