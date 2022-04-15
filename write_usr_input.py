
import os
import json
from scservo_sdk import hexa_servo_controller 
import time

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

if __name__ == '__main__':
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