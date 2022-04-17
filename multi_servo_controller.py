
import os
import json
from scservo_sdk import hexa_servo_controller 
import time
import threading
import queue
import copy

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

    def push_to_send_queue(self,servo_commu):
        self.serial_send_queue.put(servo_commu)

    def load_servo_commu_template(self):
        print("loading servo communication template")
        with open(self.servo_commu_template_file, "r") as fObj:
            self.servo_commu_template = json.load(fObj)

        print("self.servo_commu_template: " + str(self.servo_commu_template))

    def serial_servo_thread(self,name):        

        while(True):            
            servo_in_out_info = copy.deepcopy(self.servo_commu_template)
            #1. send servo params
            if (self.serial_send_queue.empty() == False):
                one_send_data = self.serial_send_queue.get()
                
                for i in one_send_data:
                    servo_id = one_send_data[i]["device_id"]
                    # send out to each servo
                    if(one_send_data[i]['send_servo_valid'] is True):
                        send_servo_pos_val =    one_send_data[i]["send_servo_pos_val"]
                        send_servo_speed_val =  one_send_data[i]["send_servo_speed_val"]
                        send_servo_torque_val = one_send_data[i]["send_servo_torque_val"]

                        servo_in_out_info[i]['send_servo_valid'] = True
                        servo_in_out_info[i]["send_servo_pos_val"] = send_servo_pos_val
                        servo_in_out_info[i]["send_servo_speed_val"] = send_servo_speed_val
                        servo_in_out_info[i]["send_servo_torque_val"] = send_servo_torque_val

                        self.servos_ctl.setTorque(send_servo_torque_val,servo_id)                
                        self.servos_ctl.setSpeed(send_servo_speed_val,servo_id)
                        self.servos_ctl.setPosition(send_servo_pos_val,servo_id)

            #2. get servo infos
            for i in servo_in_out_info:
                servo_in_out_info[i]['recv_servo_valid'] = True
                #print("Get servo index: "+ i)
                servo_id = servo_in_out_info[i]["device_id"]
                # get current pose speed
                (pose,speed) = self.servos_ctl.getPoseSpeed(servo_id)
                servo_in_out_info[i]["recv_servo_pos_val"] = pose
                servo_in_out_info[i]["recv_servo_speed_val"] = speed
                # get current torque
                servo_in_out_info[i]["recv_servo_torque_val"] = \
                    self.servos_ctl.getPresentTorque(servo_id)
                # get time
                servo_in_out_info[i]["time_stamp"] = time.monotonic()
                time_stamp = servo_in_out_info[i]["time_stamp"]

                print("servo id: "+str(servo_id)+" pose: "+str(pose)+\
                    " speed: "+str(speed)+\
                    " recv_servo_torque_val:"+\
                    str(servo_in_out_info[i]["recv_servo_torque_val"])+\
                    " time_stamp:"+str(time_stamp))
            self.serial_recv_queue.put(servo_in_out_info)

            #3. sleep a while
            self.sleep_freq_hz(10)

    def sleep_freq_hz(self,freq_hz=300):
        period_sec = 1.0/freq_hz
        time.sleep(period_sec)


def test_makeup_send_servo_commu(multi_servo_ctl):
    send_data = copy.deepcopy(multi_servo_ctl.servo_commu_template)
    for i in send_data: 
        send_data[i]['send_servo_valid'] = True
        send_data[i]['send_servo_pos_val'] = 4000
        send_data[i]['send_servo_speed_val'] = 500
        send_data[i]['send_servo_torque_val'] = 2000

if __name__ == '__main__':
    multi_servo_ctl = MultiServoController()
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
