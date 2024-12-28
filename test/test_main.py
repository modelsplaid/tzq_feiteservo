import      os
import      json
import      time
import      copy
import      math
import      queue
import      threading

from tkinter.tix               import Tree
from hexa_servo_io_controller  import MultiServoIOController

from custom_type.comu_msg_type import BotCmuMsgType

def cmput_spd(pose_old,pose_new,run_time):

    DEFAULT_SPEED   = 500
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

def test_with_valve():
    initpose = 2000
    pose_arr = [initpose,2000,1500]
    run_time_arr = [2,4]

    multi_servo_io_ctl = MultiServoIOController("servo_config.json","io_config.json")
    send_data = copy.deepcopy(multi_servo_io_ctl.svo_io_cmu_tplt)

    for j in range(1):
        # update valves 
        for i in send_data["valve_pumps"]:
            print("turn on valve pump: "+str(i) )
            send_data["valve_pumps"][i]["turn_onoff_val_pump"] = 1

            multi_servo_io_ctl.push_to_send_queue(send_data)  
            time.sleep(0.1)

        # update valves 
        for i in send_data["valve_pumps"]:
            print("turn on valve pump: "+str(i) )
            send_data["valve_pumps"][i]["turn_onoff_val_pump"] = 0

            multi_servo_io_ctl.push_to_send_queue(send_data)  
            time.sleep(0.1)   


    time.sleep(1)

    # update servos 
    for i in send_data["serial_servos"]: 
        send_data["serial_servos"][i]['send_servo_valid'] = True
        send_data["serial_servos"][i]['send_servo_pos_val'] = initpose
        send_data["serial_servos"][i]['send_servo_speed_val'] = 500
        send_data["serial_servos"][i]['send_servo_torque_val'] = 500
    multi_servo_io_ctl.push_to_send_queue(send_data)  
    # Init servo pose  
    time.sleep(5)
    print("Done init")
    print("Done init")
    print("Done init")
    time.sleep(1)
    print("start")
    # Update pose and speed
    for i in range(len(pose_arr)-1):
        #cmput_spd(initpose)
        runtime = run_time_arr[i]
        pose_val = pose_arr[i+1]
        print("pose_val:"+str(pose_val))
        (pose_servo,speed_servo) = cmput_spd(pose_arr[i],pose_val,runtime)
        for i in send_data: 
            send_data["serial_servos"][i]['send_servo_valid'] = True
            send_data["serial_servos"][i]['send_servo_pos_val'] = pose_servo
            send_data["serial_servos"][i]['send_servo_speed_val'] = speed_servo
            send_data["serial_servos"][i]['send_servo_torque_val'] = 500
        multi_servo_io_ctl.push_to_send_queue(send_data)  
        time.sleep(1)
        


def test_send_pose():
    
    multi_servo_io_ctl = MultiServoIOController("servo_config.json","io_config.json")
    while True:
        
        #send_data = copy.deepcopy(multi_servo_io_ctl.servo_io_commu_template)
        send_data = BotCmuMsgType("send_data")
        for i in range(1,send_data.num_svos+1): 
            send_data.set_snd_one_svo(i,500,1000,500)
        multi_servo_io_ctl.push_to_send_queue(send_data)        
        time.sleep(1)

        send_data = BotCmuMsgType("send_data")
        for i in range(1,send_data.num_svos+1): 
            send_data.set_snd_one_svo(i,1000,1000,500)
        multi_servo_io_ctl.push_to_send_queue(send_data)        
        time.sleep(1)

        send_data = BotCmuMsgType("send_data")
        for i in range(1,send_data.num_svos+1): 
            send_data.set_snd_one_svo(i,2000,1000,500)
        multi_servo_io_ctl.push_to_send_queue(send_data)        
        time.sleep(1)
        
        #one_frame_recv_servo = multi_servo_io_ctl.pop_recv_q_dict()
        #print("one_frame_recv_servo: "+str(one_frame_recv_servo))
        print("in main")


### todo: here add test torq direction pid 

##
##



if __name__ == '__main__':

    test_send_pose()
