
import os
import json
import time
import copy

import queue
import threading
import sys, tty, termios

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SCRIPT_DIR)

RUN_IN_SIMULATE = False


from custom_type.comu_msg_type              import BotCmuMsgType

try:
    from hexa_servo_sdk.port_handler            import * 
    from hexa_servo_sdk.sms_sts                 import *
    from hexa_servo_sdk.protocol_packet_handler import *
    from hexa_servo_sdk.hexa_servo_controller   import ServoController

except Exception as e:

    print("!!!Faild to import hexa_servo_sdk, run in simulator mode", e)
    RUN_IN_SIMULATE = True


if RUN_IN_SIMULATE == False:
    from raspi_io_sdk.valve_controller      import ValveController

# fd = sys.stdin.fileno()
# old_settings = termios.tcgetattr(fd)

print("RUN_IN_SIMULATE: ",RUN_IN_SIMULATE)
class MultiServoIOController:
    def __init__(self                                      ,\
                svo_json_cfg_fil = "servo_config.json"  ,\
                io_json_cfg_fil  = "io_config.json"     ,\
                ):
        

        # parse config params for serial servos
        with open(svo_json_cfg_fil, "r") as fObj:
            servo_config         = json.load(fObj)
            self.hwr_recv_freq   = servo_config['serial_params']["SERIAL_MAX_RECV_FREQ"]

        self.serial_recv_queue   = queue.Queue()
        self.serial_send_queue   = queue.Queue()

        if RUN_IN_SIMULATE == False:
            # parse config params for rpi4 io
            self.valpump_pump_ctl = ValveController(io_json_cfg_fil)
            self.vpump_acts       = self.valpump_pump_ctl.getValvePinoutConfigActions()        
            self.servos_ctl       = ServoController(svo_json_cfg_fil)

        self.hwr_cmu_thd          = threading.Thread(target=self.serial_servo_thread, args=(2,))
        self.hwr_cmu_thd.daemon   = True
        self.hwr_cmu_thd.start()    

    def pop_recv_q_dict(self):
        if(self.serial_recv_queue.empty()==False):
            return False
        else:    
            msg_obj   = self.serial_recv_queue.get()
            recv_dict = msg_obj.get_cmu_msg_dic()
            return recv_dict

    def push_to_send_queue(self,servo_commu):
        self.serial_send_queue.put(servo_commu)

    def serial_servo_thread(self,name):        

        glob_servo_pos = BotCmuMsgType("glob_servo_pos")

        while(True):            
            svo_io_msg = BotCmuMsgType("svo_io_msg")

            #1. send to servo msgs
            if (self.serial_send_queue.empty() == False):
                
                one_send_data_dic = self.serial_send_queue.get()
                one_send_data = BotCmuMsgType("one_send_data",one_send_data_dic)
                for i in range(1,one_send_data.get_num_svos()+1):

                    # Send out to each servo
                    if(one_send_data.get_snd_valid_stat(i) is True):

                        [pos,spd,torq,tstmp,mode] = one_send_data.get_snd_one_svo(i)

                        svo_io_msg.set_snd_one_svo(i,pos,spd,torq)
                        svo_cmu_stat = ""
                        cmu_expl = ""
                        err_msg  = ""
                        #print("servo id: ",i,"mode: ",mode,"pose val: ",pos, "spd: ",spd)
                        if RUN_IN_SIMULATE == False:
                            if(i==11):#(i==8):
                                print("i= ",i,"mode: ",mode,"torq val:",torq,"pose: ",pose )
                            # todo: check code here on set torq
                            # 1. chec if valid
                            if(pos != None):
                                if mode == "pose":
                                    # if(i == 7 or i==8 or i==9 or i == 16 or i == 17 or i == 18):
                                    #     print("mode: ",mode,"servo id: ",i,"pose val: ",pos,"torq: ",torq)
                                    torq = abs(torq)
                                    svo_cmu_stat = self.servos_ctl.setTorque(torq,i)
                                    (cmu_expl,err_msg) = self.servos_ctl.writePoseSpeed(pos,spd,i)

                                elif mode == "torq":
                                    #print("---mode: ",mode,"servo id: ",i,"pose val: ",pos,"torq: ",torq)
                                    
                                    # todo1: check right leg for the compensation
                                    # todo2: improve: compensate less for coxa joint
                                    
                                    # if(i != 15 and i!=18 and i!=9 and i != 6 and i != 3 and i != 12):
                                        
                                    #     if(torq>=0):
                                    #         pos = pos+100
                                    #     else:
                                    #         pos = pos-100    
                                            
                                    # compensate for coxa leg 
                                    if(i == 13 or i==16 or i==7 or i == 4 or i == 1 or i == 10):
                                        
                                        if(torq>=0):
                                            pos = pos-100
                                        else:
                                            pos = pos+100                                       
                                    
                                    # compensate for femur leg        
                                    if(i == 14 or i==17 or i==8 or i == 5 or i == 2 or i == 11):
                                        
                                        if(torq>=0):
                                            pos = pos-100
                                        else:
                                            pos = pos+100                                          
                                    
                                    svo_cmu_stat = self.servos_ctl.setTorque(abs(torq),i)
                                    (cmu_expl,err_msg) = self.servos_ctl.writePoseSpeed(pos,spd,i)
                                elif mode == "porq": 
                                    # set current pose to max torq
                                    
                                    [real_pos,_,_,_,_] = glob_servo_pos.get_snd_one_svo(i)
                                
                                    #print("mode: ",mode,"servo id: ",i,"target pose val: ",pos, "real pos: ", real_pos,"torq: ",torq)
                                
                                    torq = abs(torq)
                                    svo_cmu_stat = self.servos_ctl.setTorque(torq,i)
                                    (cmu_expl,err_msg) = self.servos_ctl.writePoseSpeed(real_pos,spd,i)
                            else:
                                print("!!!!!!servo id: ",i,"will not move. ")   
                                    
                            time.sleep(0.001)

                        else: 
                            cmu_expl = ""
                            err_msg  = ""
                        
                        svo_io_msg.set_snd_stat_one_svo(i,svo_cmu_stat,cmu_expl+err_msg,cmu_expl+err_msg)                        
                        time.sleep(0.001)

                #3. Set IO status  
                for i in  range(one_send_data.get_num_legs()):

                    OnOff =  one_send_data.get_ileg_vpumps(i)

                    if(RUN_IN_SIMULATE == False):
                        if  (OnOff == self.vpump_acts["turn_off"] or OnOff == self.vpump_acts["turn_on"] ):
                            #print("setting io: name: "+str(i)+" onoff: "+str(OnOff)  )
                            
                            leg_name = one_send_data.get_ileg_names(i)
                            
                            self.valpump_pump_ctl.setValveOnOffName(OnOff,leg_name)
                        elif(OnOff == self.vpump_acts["no_action"]):
                            pass
                        else:
                            print("!!! invalid parameters for io actiosn")
                            
                # update recv queue    
                svo_io_msg.set_ileg_vpumps(i,one_send_data.get_ileg_vpumps(i))    

            #2. Get servo msgs
            
            # todo: here
            for i in range(1,svo_io_msg.get_num_svos()+1):
                
                # get current pose speed
                if RUN_IN_SIMULATE == False:
                    (pose,speed,comu_rslt,comu_rslt_expn,servo_err) =\
                                                        self.servos_ctl.getPoseSpeed(i)
                    (torque_val,cmu_tq_stat) = self.servos_ctl.getPresentTorque(i)
                    
                else: 
                    pose           = 0
                    speed          = 0
                    servo_err      = "simulation"
                    comu_rslt_expn = "simulation"
                    torque_val     = 0
                    cmu_tq_stat    = "simulation"
                    
                svo_io_msg.set_rcv_one_svo(i,pose,speed,torque_val)
                svo_io_msg.set_recv_stat_one_svo(i,comu_rslt_expn+servo_err,"",cmu_tq_stat)
                svo_io_msg.set_svo_tstamp(i,time.monotonic())
                glob_servo_pos.set_snd_one_svo(i,pose)
                time.sleep(0.001)
                
            #4. Put received serial data in recv queue 
            self.serial_recv_queue.put(svo_io_msg)
            
            #5. sleep a while
            self.sleep_freq_hz(self.hwr_recv_freq)

    def sleep_freq_hz(self,freq_hz=100):
        period_sec = 1.0/freq_hz
        time.sleep(period_sec)


