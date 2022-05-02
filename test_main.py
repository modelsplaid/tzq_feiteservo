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
        '''
        send_data = copy.deepcopy(multi_servo_ctl.servo_commu_template)
        for i in send_data: 
            send_data[i]['send_servo_valid'] = True
            send_data[i]['send_servo_pos_val'] = 10
            send_data[i]['send_servo_speed_val'] = 100
            send_data[i]['send_servo_torque_val'] = 200
        multi_servo_ctl.push_to_send_queue(send_data)        
        time.sleep(1.6)


        send_data = copy.deepcopy(multi_servo_ctl.servo_commu_template)
        for i in send_data: 
            send_data[i]['send_servo_valid'] = True
            send_data[i]['send_servo_pos_val'] = 1000
            send_data[i]['send_servo_speed_val'] = 200
            send_data[i]['send_servo_torque_val'] = 500
        multi_servo_ctl.push_to_send_queue(send_data)        
        time.sleep(1.6)

        send_data = copy.deepcopy(multi_servo_ctl.servo_commu_template)
        for i in send_data: 
            send_data[i]['send_servo_valid'] = True
            send_data[i]['send_servo_pos_val'] = 2000
            send_data[i]['send_servo_speed_val'] = 300
            send_data[i]['send_servo_torque_val'] = 500
        multi_servo_ctl.push_to_send_queue(send_data)        
        time.sleep(3)
        '''
        #one_frame_recv_servo = multi_servo_ctl.pop_recv_queue()
        #print("one_frame_recv_servo: "+str(one_frame_recv_servo))
        print("in main")
        time.sleep(3)
