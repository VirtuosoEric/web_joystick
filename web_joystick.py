#!/usr/bin/env python
from flask import Flask, render_template, session, request, flash
from flask_socketio import SocketIO, emit 
from Keyence_PLC_Ethernet import Keyence_PLC_Ethernet
import time,threading

class BaseDriver:
    
    def __init__(self):
        self.max_throttle = 100
        self.max_steering = 20
        self.last_time = 0

    def connect_plc(self,ip,port):
        print ('connect to plc')
        self.plc = Keyence_PLC_Ethernet(ip,port)

    def send_cmd(self,joy_x,joy_y):
        steering = -(joy_x/100) * self.max_steering
        throttle = (joy_y/100) * self.max_throttle
        time_now = time.time()
        time_elast = time_now - self.last_time
        if time_elast > 0.3:
            print ('throttle '+ str(throttle)+' steering '+str(steering))
            data = [str(int(throttle)),str(int(steering))]
            self.plc.consecutive_write_data('DM','101','.L',data)
            self.last_time = time_now
        else:
            print('waiting')

driver = BaseDriver()


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.before_first_request
def run_once():
    driver.connect_plc('192.168.4.101',8501)
    print('hello')

@app.route('/')
def index():
    return render_template('ackerman_joystick.html')

@socketio.on('joystick_event')
def joystick_cmd(msg):
    # print(msg['steering']+' '+msg['throttle'])
    steering = float(msg['steering'])
    throttle = float(msg['throttle'])
    if steering > 100:
        steering = 100
    elif steering < -100:
        steering = -100
    if throttle > 100:
        throttle = 100
    elif throttle < -100:
        throttle = -100
    driver.send_cmd(steering,throttle)



if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0',port=5000)