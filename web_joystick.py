#!/usr/bin/env python
from flask import Flask, render_template, session, request, flash
from flask_socketio import SocketIO, emit 
from Keyence_PLC_Ethernet import Keyence_PLC_Ethernet
import time,threading,random

class BaseDriver:
    
    def __init__(self):
        self.max_throttle = 30
        self.max_steering = 60
        self.last_time = 0
        self.steering_cmd = 0.0
        self.throttle_cmd = 0.0
        self.steering_target = 0.0
        self.throttle_target = 0.0

    def connect_plc(self,ip,port):
        print ('connect to plc')
        self.id = random.randint(0,99)
        self.plc = Keyence_PLC_Ethernet(ip,port)
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
        
    def control_loop(self):
        last_loop_time = time.time()
        while True:
            time_now = time.time()
            time_elast = time_now - last_loop_time
            if time_elast > 0.3:
                self.ma(self.steering_target,self.throttle_target)
                data = [str(int(self.throttle_cmd)),str(int(self.steering_cmd))]
                print(data)
                self.plc.consecutive_write_data('DM','101','.L',data)
                # print(self.id)
                last_loop_time = time_now
                

    def send_cmd(self,joy_x,joy_y):
        steering = -(joy_x/100) * self.max_steering
        throttle = (joy_y/100) * self.max_throttle
        time_now = time.time()
        time_elast = time_now - self.last_time
        if time_elast > 0.2:
            self.ma(steering,throttle)
            print ('throttle '+ str(throttle)+' steering '+str(steering))
            data = [str(int(throttle)),str(int(steering))]
            self.plc.consecutive_write_data('DM','101','.L',data)
            self.last_time = time_now
            print(time_elast)
        else:
            pass
            # print('waiting')

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
    # driver.send_cmd(steering,throttle)
    driver.update_target(steering,throttle)



if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0',port=5000)