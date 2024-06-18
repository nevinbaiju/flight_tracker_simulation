# # app.py

# from flask import Flask, render_template
# from flask_socketio import SocketIO, emit
# from flask_cors import CORS
import redis
# import json

# app = Flask(__name__)
# CORS(app)  # Enable CORS for all routes
# socketio = SocketIO(app, cors_allowed_origins="*")  # Enable CORS for SocketIO

# redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

# def listen_to_redis():
#     pubsub = redis_client.pubsub()
#     pubsub.subscribe('flight_updates')  # Channel name for flight updates

#     for message in pubsub.listen():
#         if message['type'] == 'message':
#             flight_data = json.loads(message['data'])
#             print('Emitting flight update:', flight_data)
#             socketio.emit('flight_update', flight_data, namespace='/flights')

# @app.route('/')
# def index():
#     return render_template('index.html')

# if __name__ == '__main__':
#     socketio.start_background_task(target=listen_to_redis)
#     socketio.run(app, debug=True)


from flask import Flask, render_template
from flask_socketio import SocketIO

import redis
import json
import time

app = Flask(__name__)
socketio = SocketIO(app)
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

@app.route('/')
def index():
    return render_template('index.html')

def background_task():
    """Background task that sends 'hi' every second."""
    while True:
        time.sleep(0.1)

            # Connect to the Redis server
        client = redis.Redis(host='localhost', port=6379, db=0)
        keys = client.keys('*')
        flights = []
        for key in keys:
            value = client.get(key)
            try:
                value = json.loads(value.decode('utf-8'))
            except (json.JSONDecodeError, AttributeError):
                value = value.decode('utf-8')
            except:
                continue
            value['flight_id'] = key.decode("utf-8")
            flights.append(value)
            
        socketio.emit('update', json.dumps(flights), namespace='/flights')

@socketio.on('connect', namespace='/flights')
def handle_connect():
    print('Client connected')
    socketio.start_background_task(background_task)

@socketio.on('disconnect', namespace='/flights')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, debug=True)
