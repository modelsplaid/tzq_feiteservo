import os
import json
from tkinter.tix import Tree
from hexa_servo_sdk import hexa_servo_controller 
import time
import threading
import queue
import copy
import math

def test_send_pose():
    multi_servo_ctl = hexa_servo_controller.\
        MultiServoController("servo_config.json","servo_commu.json")
    while True:
        
        send_data = copy.deepcopy(multi_servo_ctl.servo_commu_template)
        for i in send_data: 
            send_data[i]['send_servo_valid'] = True
            send_data[i]['send_servo_pos_val'] = 500
            send_data[i]['send_servo_speed_val'] = 1000
            send_data[i]['send_servo_torque_val'] = 500
        multi_servo_ctl.push_to_send_queue(send_data)        
        time.sleep(1)


        send_data = copy.deepcopy(multi_servo_ctl.servo_commu_template)
        for i in send_data: 
            send_data[i]['send_servo_valid'] = True
            send_data[i]['send_servo_pos_val'] = 1000
            send_data[i]['send_servo_speed_val'] = 1000
            send_data[i]['send_servo_torque_val'] = 500
        multi_servo_ctl.push_to_send_queue(send_data)        
        time.sleep(1)

        send_data = copy.deepcopy(multi_servo_ctl.servo_commu_template)
        for i in send_data: 
            send_data[i]['send_servo_valid'] = True
            send_data[i]['send_servo_pos_val'] = 2000
            send_data[i]['send_servo_speed_val'] = 1000
            send_data[i]['send_servo_torque_val'] = 500
        multi_servo_ctl.push_to_send_queue(send_data)        
        time.sleep(1)
        
        #one_frame_recv_servo = multi_servo_ctl.pop_recv_queue()
        #print("one_frame_recv_servo: "+str(one_frame_recv_servo))
        print("in main")



def compute_speed(pose_old,pose_new,run_time):
    DEFAULT_SPEED = 500
    VALID_MIN_SPEED = 1
    VALID_MAX_SPEED = 3000
    pose_diffs = abs(pose_new-pose_old) 
    if(pose_diffs <= 0): 
        speed_new = DEFAULT_SPEED
        print("!!!Invalid servo pose diffs, use default speed")
        return (pose_new,speed_new)
    if(run_time <= 0):
        speed_new = DEFAULT_SPEED
        print("!!!Invalid servo speed, use default speed")
        return (pose_new,speed_new)
    
    speed_new = (pose_diffs)/run_time
    speed_new = int(speed_new)
    #todo: check speed valid    
    if((VALID_MIN_SPEED > speed_new) or (VALID_MAX_SPEED < speed_new)):
        print("!!!Calculated speed out of valid range, use default speed")
        speed_new = DEFAULT_SPEED
        return (pose_new,speed_new)

    return (pose_new,speed_new)


if __name__ == '__main__':
    initpose = 1000
    pose_arr = [initpose,2000,4000]
    run_time_arr = [2,4]

    multi_servo_ctl = hexa_servo_controller.\
    MultiServoController("servo_config.json","servo_commu.json")
    send_data = copy.deepcopy(multi_servo_ctl.servo_commu_template)

    for i in send_data: 
        send_data[i]['send_servo_valid'] = True
        send_data[i]['send_servo_pos_val'] = initpose
        send_data[i]['send_servo_speed_val'] = 1500
        send_data[i]['send_servo_torque_val'] = 500
    multi_servo_ctl.push_to_send_queue(send_data)  
    # Init servo pose  
    time.sleep(5)
    print("Done init")
    print("Done init")
    print("Done init")
    time.sleep(1)
    print("start")
    while True:
        # Update pose and speed
        for i in range(len(pose_arr)-1):
            #compute_speed(initpose)
            runtime = run_time_arr[i]
            pose_val = pose_arr[i+1]
            print("pose_val:"+str(pose_val))
            (pose_servo,speed_servo) = compute_speed(pose_arr[i],pose_val,runtime)
            for i in send_data: 
                send_data[i]['send_servo_valid'] = True
                send_data[i]['send_servo_pos_val'] = pose_servo
                send_data[i]['send_servo_speed_val'] = speed_servo
                send_data[i]['send_servo_torque_val'] = 500
            multi_servo_ctl.push_to_send_queue(send_data)  
            time.sleep(runtime)
        exit()