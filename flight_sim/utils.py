import random
import string
import math
import datetime
import time
import logging

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S %Z'
EARTH_RADIUS_KM = 6371.0
AVG_FLIGHT_SPEED = 5
DELAY = 0.5

def setup_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create a formatter and set it to the handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    
    # Add the handler to the logger
    logger.addHandler(console_handler)
    
    return logger

def generate_random_username(length=8):
    """Generate a random username with the given length."""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def generate_random_coordinates():
    """Generates random coordinates on Earth."""
    latitude = random.uniform(-90.0, 90.0)
    longitude = random.uniform(-180.0, 180.0)
    return latitude, longitude

def euclidean_distance(coord1, coord2):
    """Calculates Euclidean distance between two coordinates."""
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    
    return math.sqrt((lon1 - lon2)**2 + (lat1-lat2)**2)

def generate_fligh_path():
    """Generates a list of flight paths with random coordinates."""
    start = generate_random_coordinates()
    # Introduce variation in distances (intra-country and inter-country)
    if random.random() < 0.7:
        # Intra-country (shorter distances)
        end = (
            start[0] + random.uniform(-5, 5),
            start[1] + random.uniform(-5, 5)
        )
    else:
        # Inter-country (longer distances)
        end = generate_random_coordinates()
    distance = euclidean_distance(start, end)
    flight = {
        'flight_id': generate_random_username(),
        'start': start,
        'curr': start,
        'end': end,
        'distance_km': distance,
        'start_time': datetime.datetime.now(datetime.timezone.utc).strftime(DATETIME_FORMAT),
        'landed': False
    }
    
    return flight

def find_x_y(hypotenuse, start, end):
    lat1, long1 = start
    lat2, long2 = end
    c = hypotenuse
    m = (long2-long1)/(lat2-lat1)    
    theta = math.atan(m)
    
    adj = c * math.cos(theta)
    opp = c * math.sin(theta)

    new_lat = lat1-adj if lat2 < lat1 else lat1+adj
    new_long = long1-opp if long2 < long1 else long1+opp
    
    return lat1+adj, long1+opp

# Function to calculate current position based on start, end, start_time, and current_time
def get_current_position(flight):
    start = flight['start']
    end = flight['end']
    start_time = datetime.datetime.strptime(flight['start_time'], DATETIME_FORMAT).replace(tzinfo=datetime.timezone.utc)
    current_time = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=datetime.timezone.utc)
    
    elapsed_time_hours = (current_time - start_time).total_seconds() / 3600
    
    distance_traveled = 400 * elapsed_time_hours

    if distance_traveled >= flight['distance_km']:
        return True, flight['end']

    return False, find_x_y(distance_traveled, start, end)