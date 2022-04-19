import os
import json
from hexa_servo_sdk import hexa_servo_controller 
import time
import threading
import queue
import copy

if __name__ == '__main__':
    multi_servo_ctl = hexa_servo_controller.MultiServoController()
    while True: 
        send_data = copy.deepcopy(multi_servo_ctl.servo_commu_template)
        for i in send_data: 
            send_data[i]['send_servo_valid'] = True
            send_data[i]['send_servo_pos_val'] = 2000
            send_data[i]['send_servo_speed_val'] = 500
            send_data[i]['send_servo_torque_val'] = 200
        multi_servo_ctl.push_to_send_queue(send_data)        
        time.sleep(5)


        send_data = copy.deepcopy(multi_servo_ctl.servo_commu_template)
        for i in send_data: 
            send_data[i]['send_servo_valid'] = True
            send_data[i]['send_servo_pos_val'] = 000
            send_data[i]['send_servo_speed_val'] = 1000
            send_data[i]['send_servo_torque_val'] = 500
        multi_servo_ctl.push_to_send_queue(send_data)        
        time.sleep(5)

        print("in main")