
import sys, tty, termios
import os
import json
from .port_handler import * 
from .packet_handler import *
import time
import threading
import queue
import copy

fd = sys.stdin.fileno()
old_settings = termios.tcgetattr(fd)

def getch():
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


class ServoController:
    
    def __init__(self,servo_config_file = "servo_config.json"):    
        self.parseServoConfig(servo_config_file)
        self.openPort()
    def openPort(self):        
        # Initialize PortHandler instance
        # Set the port path
        # Get methods and members of PortHandlerLinux or PortHandlerWindows
        self.portHandler = PortHandler(self.DEVICENAME)

        # Initialize PacketHandler instance
        # Get methods and members of Protocol
        self.packetHandler = PacketHandler(self.protocol_end)

        # Open port
        if self.portHandler.openPort():
            print("Succeeded to open the port")
        else:
            print("Failed to open the port")
            print("Press any key to terminate...")
            getch()
            quit()

        # Set port baudrate
        if self.portHandler.setBaudRate(self.BAUDRATE):
            print("Succeeded to change the baudrate")
        else:
            print("Failed to change the baudrate")
            print("Press any key to terminate...")
            getch()
            quit()
    def parseServoConfig(self,file_name = "servo_config.json" ):
        with open(file_name, "r") as fObj:
            servo_config = json.load(fObj)
            #print("servo_config:")
            #print(servo_config)

            #1. parse serial params
            self.BAUDRATE = servo_config['serial_params']['BAUDRATE']
            self.DEVICENAME = servo_config['serial_params']['DEVICENAME']

            #3. parse servo params 
            self.SCS_MINIMUM_POSITION_VALUE = servo_config['servo_params']['SCS_MINIMUM_POSITION_VALUE']
            self.SCS_MAXIMUM_POSITION_VALUE = servo_config['servo_params']['SCS_MAXIMUM_POSITION_VALUE']
            self.SCS_MOVING_STATUS_THRESHOLD = servo_config['servo_params']['SCS_MOVING_STATUS_THRESHOLD']
            self.SCS_MOVING_SPEED = servo_config['servo_params']['SCS_MOVING_SPEED']
            self.SCS_MOVING_ACC = servo_config['servo_params']['SCS_MOVING_ACC']
            self.protocol_end = servo_config['servo_params']['protocol_end']

            #4. parse servo control table 
            self.ADDR_SCS_TORQUE_ENABLE = servo_config['servo_control_table']['ADDR_SCS_TORQUE_ENABLE']
            self.ADDR_SCS_GOAL_ACC = servo_config['servo_control_table']['ADDR_SCS_GOAL_ACC']
            self.ADDR_SCS_GOAL_POSITION = servo_config['servo_control_table']['ADDR_SCS_GOAL_POSITION']
            self.ADDR_SCS_GOAL_SPEED = servo_config['servo_control_table']['ADDR_SCS_GOAL_SPEED']
            self.ADDR_SCS_PRESENT_POSITION = servo_config['servo_control_table']['ADDR_SCS_PRESENT_POSITION']

            self.ADDR_TORQUE_LIMIT = servo_config['servo_control_table']['ADDR_TORQUE_LIMIT']
            self.ADDR_CURRENT_TORQUE_VAL = servo_config['servo_control_table']['ADDR_CURRENT_TORQUE_VAL']
    
    def setTorque(self,torque_val=200,servo_id = 1):
        # Write SCServo speed
        scs_comm_result, scs_error = self.packetHandler.write2ByteTxRx\
            (self.portHandler, servo_id, self.ADDR_TORQUE_LIMIT, torque_val)
        if scs_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(scs_comm_result))
        elif scs_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(scs_error))

    
    def setAcc(self,servo_id = 1):
        # Write SCServo acc
        scs_comm_result, scs_error = self.packetHandler.write1ByteTxRx(\
            self.portHandler, servo_id, self.ADDR_SCS_GOAL_ACC, self.SCS_MOVING_ACC)
        if scs_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(scs_comm_result))
        elif scs_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(scs_error))

    def setSpeed(self,speed_val=0,servo_id = 1):

        # Write SCServo speed
        scs_comm_result, scs_error = self.packetHandler.write2ByteTxRx\
            (self.portHandler, servo_id, self.ADDR_SCS_GOAL_SPEED, speed_val)
        if scs_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(scs_comm_result))
        elif scs_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(scs_error))

    def setPosition(self,position_val=0,servo_id = 1):

            # Write SCServo goal position
            scs_comm_result, scs_error = \
                self.packetHandler.write2ByteTxRx\
                (self.portHandler, servo_id, self.ADDR_SCS_GOAL_POSITION,position_val)
            if scs_comm_result != COMM_SUCCESS:
                print("%s" % self.packetHandler.getTxRxResult(scs_comm_result))
            elif scs_error != 0:
                print("%s" % self.packetHandler.getRxPacketError(scs_error))

    def getPresentTorque(self,servo_id = 1):
        # Write SCServo goal position
        torque_val,result, scs_error = \
            self.packetHandler.read2ByteTxRx\
            (self.portHandler, servo_id, self.ADDR_CURRENT_TORQUE_VAL)

        torque_val = SCS_TOHOST(torque_val, 10)

        if result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(result))
        elif scs_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(scs_error))
        #print("Present torque: %03d"%( torque_val))

        return torque_val

    def getPoseSpeed(self,servo_id = 1):
        
        scs_present_position_speed, scs_comm_result, scs_error =\
            self.packetHandler.read4ByteTxRx(\
            self.portHandler, servo_id, self.ADDR_SCS_PRESENT_POSITION)
        if scs_comm_result != COMM_SUCCESS:
            print(self.packetHandler.getTxRxResult(scs_comm_result))
        elif scs_error != 0:
            print(self.packetHandler.getRxPacketError(scs_error))

        scs_present_position = SCS_LOWORD(scs_present_position_speed)
        scs_present_speed = SCS_HIWORD(scs_present_position_speed)
        scs_present_speed = SCS_TOHOST(scs_present_speed, 15)
        #print("[ID:%03d] PresPos:%03d PresSpd:%03d"%\
        #     (servo_id, scs_present_position,scs_present_speed))
        return (scs_present_position,scs_present_speed)

    def deactivateTorque(self,servo_id = 1):

        scs_comm_result, scs_error = self.packetHandler.write1ByteTxRx(\
            self.portHandler, servo_id, self.ADDR_SCS_TORQUE_ENABLE, 0)
        if scs_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(scs_comm_result))
        elif scs_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(scs_error))

    def closePort(self):
        # Close port
        self.portHandler.closePort()

class MultiServoController:
    def __init__(self,\
                servo_json_config_file = "servo_config.json",\
                serial_max_recv_freq=50,\
                servo_commu_template_file = "servo_commu.json"\
                ):
        self.serial_max_recv_freq = serial_max_recv_freq
        self.servo_commu_template_file = servo_commu_template_file
        self.servo_commu_template = None
        self.serial_recv_queue = queue.Queue()
        self.serial_send_queue = queue.Queue()

        self.load_servo_commu_template()
        self.servos_ctl = ServoController(servo_json_config_file)

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
            self.sleep_freq_hz(self.serial_max_recv_freq)

    def sleep_freq_hz(self,freq_hz=100):
        period_sec = 1.0/freq_hz
        time.sleep(period_sec)
