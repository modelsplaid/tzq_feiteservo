
import os
import json
from scservo_sdk import hexa_servo_controller 
import time
import threading
import queue

if os.name == 'nt':
    import msvcrt
    def getch():
        return msvcrt.getch().decode()
        
else:
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    def getch():
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

class MultiServoController:
    def __init__(self,\
                servo_json_config_file = "servo_config.json",\
                serial_send_freq=300,\
                servo_commu_template_file = "servo_commu.json"\
                ):
        self.serial_send_freq = serial_send_freq
        self.servo_commu_template_file = servo_commu_template_file
        self.servo_commu_template = None
        self.serial_recv_queue = queue.Queue()
        self.serial_send_queue = queue.Queue()

        self.load_servo_commu_template()
        self.servos_ctl = hexa_servo_controller.servo_controller(servo_json_config_file)

        self.serial_commu_thread = threading.Thread(target=self.serial_servo_thread, args=(2,))
        self.serial_commu_thread.daemon = True
        self.serial_commu_thread.start()    
        


    
    def load_servo_commu_template(self):
        print("loading servo communication template")
        with open(self.servo_commu_template_file, "r") as fObj:
            self.servo_commu_template = json.load(fObj)

        print("self.servo_commu_template: " + str(self.servo_commu_template))

    def serial_servo_thread(self,name):        
        while(True):

            if (self.serial_send_queue.empty()==False):
                pass
            #1. set servo params

            #2. get servo infos

            #3. sleep a while
            self.sleep_freq_hz()

    def sleep_freq_hz(self,freq_hz=300):
        period_sec = 1.0/freq_hz
        time.sleep(period_sec)


def oldservo():
    
    servoCtl = hexa_servo_controller.servo_controller()
    while (True):
        user_msg = input("Input servo id position speed torque : ")
        servo_id = int(user_msg[0])    
        servo_pose = int(user_msg[1])*1000
        servo_speed = int(user_msg[2])*200
        servo_torque = int(user_msg[3])*100
                
        
        if user_msg == chr(0x1b):
            break            

        print("User given servo_id: "+str(servo_id))
        print("User given position: "+str(servo_pose))
        print("User given speed: "+str(servo_speed))
        print("User given servo_torque: "+str(servo_torque))

        

        servoCtl.setPosition(servo_pose,servo_id)
        servoCtl.setSpeed(servo_speed,servo_id)
        servoCtl.getPoseSpeed(servo_id)
        servoCtl.setTorque(servo_torque,servo_id)
        for i in range(100): 
            time.sleep(0.1)
            servoCtl.getPoseSpeed(servo_id)
            servoCtl.getPresentTorque(servo_id)

if __name__ == '__main__':
    multi_servo_ctl = MultiServoController()
