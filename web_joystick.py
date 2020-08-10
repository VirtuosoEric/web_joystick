#!/usr/bin/env python
from flask import Flask, render_template, session, request, flash
from flask_socketio import SocketIO, emit 
import time
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('simple_joystick.html')

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0',port=5000)