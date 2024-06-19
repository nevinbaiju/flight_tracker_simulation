from flask import Flask, render_template, request
from flask_socketio import SocketIO

import redis
import json
import time
import os
import threading

redis_host = os.getenv('REDIS_HOST')
redis_port = int(os.getenv('REDIS_PORT'))
redis_password = os.getenv('REDIS_PASSWORD')

app = Flask(__name__)
socketio = SocketIO(app)
start_task = threading.Event()
start_task.clear()
connected_clients = 0
lock = threading.Lock()

redis_client = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password)

@app.route('/')
def index():
    return render_template('index.html')

def background_task():
    global connected_clients, start_task
    while start_task.is_set() and connected_clients:
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
    global start_task, connected_clients
    with lock:
        connected_clients += 1
        if connected_clients == 1:
            start_task.set()
            socketio.start_background_task(background_task)

@socketio.on('disconnect', namespace='/flights')
def handle_disconnect():
    global start_task, connected_clients
    with lock:
        connected_clients -= 1
        if connected_clients == 0:
            start_task.clear()

if __name__ == '__main__':
    socketio.run(app, debug=True)
