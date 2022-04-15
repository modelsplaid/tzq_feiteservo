
import os
import json
from scservo_sdk import hexa_servo_controller 
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
        user_msg = input("Input servo speed position id: ")
        servo_speed = int(user_msg[0])*200            
        servo_pose = int(user_msg[1])*1000
        servo_id = int(user_msg[2])*1000            
        if user_msg == chr(0x1b):
            break            

        print("User given speed: "+str(servo_speed))
        print("User given position: "+str(servo_pose))
        print("User given servo_id: "+str(servo_id))

        servoCtl.setPosition(servo_pose,servo_id)
        servoCtl.setSpeed(servo_speed,servo_id)
        servoCtl.getPoseSpeed(servo_id)