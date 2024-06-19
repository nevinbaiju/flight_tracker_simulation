from flask import Flask, render_template
from flask_socketio import SocketIO

import redis
import json
import time
import os

redis_host = os.getenv('REDIS_HOST')
redis_port = int(os.getenv('REDIS_PORT'))
redis_password = os.getenv('REDIS_PASSWORD')

print(redis_host, redis_port, redis_password)

app = Flask(__name__)
socketio = SocketIO(app)
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password)

@app.route('/')
def index():
    return render_template('index.html')

def background_task():
    """Background task that sends 'hi' every second."""
    while True:
        time.sleep(0.1)

            # Connect to the Redis server
        keys = redis_client.keys('*')
        flights = []
        for key in keys:
            value = redis_client.get(key)
            try:
                value = json.loads(value.decode('utf-8'))
            except (json.JSONDecodeError, AttributeError):
                try:
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
