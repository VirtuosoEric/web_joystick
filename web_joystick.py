#!/usr/bin/env python
from flask import Flask, render_template, session, request, flash
from flask_socketio import SocketIO, emit 
from PLC_UDP import PLC_UDP
import time,threading,random

class BaseDriver:
    
    def __init__(self):
        self.max_throttle = 30
        self.max_steering = 15
        self.last_time = 0
        self.steering_cmd = 0.0
        self.throttle_cmd = 0.0
        self.steering_target = 0.0
        self.throttle_target = 0.0

    def connect_plc(self,ip,port):
        print ('connect to plc')
        self.id = random.randint(0,99)
        self.plc = PLC_UDP(ip,port)
        t = threading.Thread(target=self.control_loop)
        t.daemon = True
        t.start()

    def ma(self,steering,throttle):
        self.steering_cmd = self.steering_cmd*0.8 + steering*0.2
        self.throttle_cmd = self.throttle_cmd*0.8 + throttle*0.2
        # print ('throttle_cmd '+ str(self.throttle_cmd)+' steering_cmd '+str(self.steering_cmd))

    def update_target(self,joy_x,joy_y):
        steering = -(joy_x/100) * self.max_steering
        throttle = (joy_y/100) * self.max_throttle
        self.steering_target = steering
        self.throttle_target = throttle
        # print ('throttle_target '+ str(self.throttle_target)+' steering_target '+str(self.steering_target))

    def motion_cmd(self):
        if self.throttle_target > 0:
            self.plc.force_set('MR','504')
            self.plc.force_reset('MR','505')
        elif self.throttle_target < 0:
            self.plc.force_reset('MR','504')
            self.plc.force_set('MR','505')
        # elif self.throttle_target == 0:
        #     self.plc.write_data('DM')
        throttle_cmd = 499 - abs(self.throttle_target*10)
        if throttle_cmd < -499:
            throttle_cmd = -499
        self.plc.write_data('DM','50','.U',str(int(throttle_cmd)))
        self.plc.write_data('DM','51','.U',str(int(throttle_cmd)))
        self.plc.write_data('DM','52','.L',str(int(self.steering_target)))
        print('sterring_cmd=',int(self.steering_target))
        print('throttle_cmd=',int(throttle_cmd))
            
        
    def control_loop(self):
        last_loop_time = time.time()
        while True:
            time_now = time.time()
            time_elast = time_now - last_loop_time
            if time_elast > 0.3:
                self.motion_cmd()
                last_loop_time = time_now
                

driver = BaseDriver()


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.before_first_request
def run_once():
    driver.connect_plc('192.168.30.15',8501)
    print('heeeeeeeeeeeeeello')

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
    driver.update_target(steering,throttle)



if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0',port=5000)