
import os
import json
import time
import copy
import queue
import threading
import sys, tty, termios

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SCRIPT_DIR)

from hexa_servo_sdk.port_handler            import * 
from hexa_servo_sdk.sms_sts                 import *
from hexa_servo_sdk.protocol_packet_handler import *
from hexa_servo_sdk.hexa_servo_controller   import ServoController

from custom_type.comu_msg_type              import BotCmuMsgType

RUN_IN_SIMULATE = True

if RUN_IN_SIMULATE == False:
    from raspi_io_sdk.valve_controller      import ValveController

fd = sys.stdin.fileno()
old_settings = termios.tcgetattr(fd)

class MultiServoIOController:
    def __init__(self                                      ,\
                svo_json_cfg_fil    = "servo_config.json"  ,\
                io_svo_cmu_tplt_fil = "servo_io_commu.json",\
                io_json_cfg_fil     = "io_config.json"     ,\
                ):
        

        # parse config params for serial servos
        with open(svo_json_cfg_fil, "r") as fObj:
            servo_config         = json.load(fObj)
            self.hwr_recv_freq   = servo_config['serial_params']["SERIAL_MAX_RECV_FREQ"]

        self.io_svo_cmu_tplt_fil = io_svo_cmu_tplt_fil
        self.svo_io_cmu_tplt     = None
        self.serial_recv_queue   = queue.Queue()
        self.serial_send_queue   = queue.Queue()

        self.load_servo_commu_template()

        if RUN_IN_SIMULATE == False:
            # parse config params for rpi4 io
            self.valpump_pump_ctl    = ValveController(io_json_cfg_fil)
            self.io_actions          = self.valpump_pump_ctl.getValvePinoutConfigActions()        
            self.servos_ctl          = ServoController(svo_json_cfg_fil)

        self.hwr_cmu_thd         = threading.Thread(target=self.serial_servo_thread, args=(2,))
        self.hwr_cmu_thd.daemon  = True
        self.hwr_cmu_thd.start()    

    def pop_recv_queue(self):
        if(self.serial_recv_queue.empty()==False):
            return False
        else:    
            return self.serial_recv_queue.get()

    def push_to_send_queue(self,servo_commu):
        self.serial_send_queue.put(servo_commu)

    def load_servo_commu_template(self):
        print("loading servo communication template")
        with open(self.io_svo_cmu_tplt_fil, "r") as fObj:
            self.svo_io_cmu_tplt = json.load(fObj)
        #print("self.svo_io_cmu_tplt: " + str(self.svo_io_cmu_tplt))

    def serial_servo_thread(self,name):        

        while(True):            
            servo_in_out_info = BotCmuMsgType("servo_in_out_info")

            #1. send to servo msgs
            if (self.serial_send_queue.empty() == False):

                
                one_send_data = self.serial_send_queue.get()

                one_send_data = BotCmuMsgType("temperal")

                
                for i in range(1,one_send_data.num_svos+1):

                    servo_id = one_send_data["serial_servos"][i]["device_id"]
                    #print("Set servo index: "+ i)
                    # send out to each servo
                    if(one_send_data.get_snd_valid_stat(i) is True):


                        [pos,spd,torq] = one_send_data.get_snd_one_svo(i)


                        servo_in_out_info.set_snd_one_svo(i,pos,spd,torq)


                        if RUN_IN_SIMULATE == False:
                            servo_and_commu_stats = self.servos_ctl.setTorque(torq,i)

                        
                        # todo: here: 
                        # todo: here: 
                        # todo: here: 
                        # todo: here: 

                        servo_in_out_info["serial_servos"][i]["send_servo_torque_stats"] = servo_and_commu_stats
                        time.sleep(0.001)

                        if RUN_IN_SIMULATE == False:
                            (scs_comm_expl,scs_svo_err_expl) = self.servos_ctl.writePoseSpeed(pos,spd,i)
                        else: 
                            scs_comm_expl    = ""
                            scs_svo_err_expl = ""

                        servo_in_out_info["serial_servos"][i]["send_servo_pos_stats"] =\
                             scs_comm_expl + scs_svo_err_expl

                        servo_in_out_info["serial_servos"][i]["send_servo_speed_stats"] =\
                             scs_comm_expl + scs_svo_err_expl

                        time.sleep(0.001)

                #3. Set IO status  
                for i in  one_send_data["valve_pumps"]:
                    #"turn_onoff_val_pump" : 0: Turn off valve and pump,
                    #                        1: Turn on valve and pump 
                    #                        2: No action 
                    OnOff =  one_send_data["valve_pumps"][i]["turn_onoff_val_pump"] 

                    if  (OnOff == self.io_actions["turn_off"] or OnOff == self.io_actions["turn_on"] ):
                        #print("setting io: name: "+str(i)+" onoff: "+str(OnOff)  )
                        self.valpump_pump_ctl.setValveOnOffName(OnOff,i)

                    elif(OnOff == self.io_actions["no_action"]):
                        pass
                    else:
                        print("!!! invalid parameters for io actiosn")

                # update recv queue        
                servo_in_out_info["valve_pumps"] = one_send_data["valve_pumps"]

            #2. Get servo msgs
            for i in servo_in_out_info["serial_servos"]:
                
                servo_in_out_info["serial_servos"][i]['recv_servo_valid'] = True
                #print("Get servo index: "+ i)
                servo_id = servo_in_out_info["serial_servos"][i]["device_id"]
                # get current pose speed

                
                if RUN_IN_SIMULATE == False:
                    (pose,speed,comm_result,comm_result_explain,servo_err) =\
                            self.servos_ctl.getPoseSpeed(servo_id)
                else: 
                    pose                = 0
                    speed               = 0
                    servo_err           = "simulation"
                    comm_result_explain = "simulation"


                servo_in_out_info["serial_servos"][i]["recv_servo_pos_val"]     = pose
                servo_in_out_info["serial_servos"][i]["recv_servo_speed_val"]   = speed
                servo_in_out_info["serial_servos"][i]["recv_servo_pos_stats"]   = comm_result_explain+servo_err
                servo_in_out_info["serial_servos"][i]["recv_servo_speed_stats"] = comm_result_explain+servo_err
                time.sleep(0.001)

                if RUN_IN_SIMULATE == False:
                    (torque_val,commu_and_servo_stat) = self.servos_ctl.getPresentTorque(servo_id)
                else: 
                    torque_val           = 0
                    commu_and_servo_stat = "simulation"

                # get current torque
                servo_in_out_info["serial_servos"][i]["recv_servo_torque_val"]   = torque_val
                servo_in_out_info["serial_servos"][i]["recv_servo_torque_stats"] = commu_and_servo_stat
                #print("torque_val: "+str(torque_val) )
                
                # get time
                servo_in_out_info["serial_servos"][i]["time_stamp"] = time.monotonic()
                time_stamp = servo_in_out_info["serial_servos"][i]["time_stamp"]

                time.sleep(0.001)
                #print("servo id: "+str(servo_id)+" pose: "+str(pose)+\
                #    " speed: "+str(speed)+\
                #    " recv_servo_torque_val:"+\
                #    str(servo_in_out_info[i]["recv_servo_torque_val"])+\
                #    " time_stamp:"+str(time_stamp))
                
            #4. Put received serial data in recv queue 
            self.serial_recv_queue.put(servo_in_out_info)
            
            #5. sleep a while
            self.sleep_freq_hz(self.hwr_recv_freq)

    def sleep_freq_hz(self,freq_hz=100):
        period_sec = 1.0/freq_hz
        time.sleep(period_sec)


