
import sys, tty, termios
import os
import json
from .port_handler import * 
from .sms_sts import *
from .protocol_packet_handler import *
import time
import threading
import queue
import copy

# fd = sys.stdin.fileno()
# old_settings = termios.tcgetattr(fd)

# def getch():
#     try:
#         tty.setraw(sys.stdin.fileno())
#         ch = sys.stdin.read(1)
#     finally:
#         termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
#     return ch


class ServoController:
    
    def __init__(self,servo_config_file = "servo_config.json"):    
        self.parseServoConfig(servo_config_file)
        self.openPort()
        #self.SCS_MOVING_ACC              = 250          # SCServo moving acc
    def openPort(self):        
        # Initialize PortHandler instance
        # Set the port path
        # Get methods and members of PortHandlerLinux or PortHandlerWindows
        print("Initializing serial port...")
        self.portHandler = PortHandler(self.DEVICENAME)
        # Initialize PacketHandler instance
        # Get methods and members of Protocol
        self.packetHandler = sms_sts(self.portHandler)

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
        
        print("Done")


    def parseServoConfig(self,file_name = "servo_config.json" ):
        with open(file_name, "r") as fObj:
            servo_config = json.load(fObj)
            print("servo_config params:")
            print(servo_config)

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
    
    def writePoseSpeed(self,position_val=0,speed_val=0,servo_id = 1):
        #print("servo id: "+str(servo_id)+"write_pose: psoe: "+str(position_val)+ " speed val: "+str(speed_val)+"acc: " +str(self.SCS_MOVING_ACC))
        scs_comm_result, scs_error = self.packetHandler.WritePosEx(servo_id, position_val, speed_val,self.SCS_MOVING_ACC)
        scs_comm_result_explain = ''
        scs_servo_stat_err_explain = ''

        if scs_comm_result != COMM_SUCCESS:
            scs_comm_result_explain = self.packetHandler.getTxRxResult(scs_comm_result)
            print("%s" % self.packetHandler.getTxRxResult(scs_comm_result))
        elif scs_error != 0:
            scs_servo_stat_err_explain = self.packetHandler.getRxPacketError(scs_error)
            print("%s" % self.packetHandler.getRxPacketError(scs_error))

        return (scs_comm_result_explain,scs_servo_stat_err_explain)

    def setTorque(self,torque_val=200,servo_id = 1):
        # Write SCServo speed
        scs_comm_result, scs_error = self.packetHandler.write2ByteTxRx\
            (servo_id, self.ADDR_TORQUE_LIMIT, torque_val)
        TxRxResult = ''
        packet_status = ''
        if scs_comm_result != COMM_SUCCESS:
            TxRxResult = self.packetHandler.getTxRxResult(scs_comm_result)
            print("%s" %TxRxResult) 
        elif scs_error != 0:
            packet_status = self.packetHandler.getRxPacketError(scs_error)
            print("%s" %packet_status)
            
        return TxRxResult+packet_status

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
            ( servo_id, self.ADDR_SCS_GOAL_SPEED, speed_val)
        if scs_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(scs_comm_result))
        elif scs_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(scs_error))

    def setPosition(self,position_val=0,servo_id = 1):

            # Write SCServo goal position
            scs_comm_result, scs_error = \
                self.packetHandler.write2ByteTxRx\
                ( servo_id, self.ADDR_SCS_GOAL_POSITION,position_val)
            if scs_comm_result != COMM_SUCCESS:
                print("%s" % self.packetHandler.getTxRxResult(scs_comm_result))
            elif scs_error != 0:
                print("%s" % self.packetHandler.getRxPacketError(scs_error))

    def getPresentTorque(self,servo_id = 1):
        # Write SCServo goal position
        torque_val,result, scs_error = \
            self.packetHandler.read2ByteTxRx\
            (servo_id, self.ADDR_CURRENT_TORQUE_VAL)
        torque_val = self.packetHandler.scs_tohost(torque_val, 10)
        commu_stat = ''
        servo_stat = ''
        if result != COMM_SUCCESS:
            commu_stat = self.packetHandler.getTxRxResult(result)
            print("%s" % commu_stat)
        elif scs_error != 0:
            servo_stat = self.packetHandler.getRxPacketError(scs_error)
            print("%s" % servo_stat)
        #print("Present torque: %03d"%( torque_val))
        commu_and_servo_stat = commu_stat + servo_stat

        return (torque_val,commu_and_servo_stat)

    def getPoseSpeed(self,servo_id = 1):

        # Read SCServo present position
        scs_comm_result_explain = ''
        scs_servo_stat_err_explain = ''
        scs_present_position, scs_present_speed, scs_comm_result, scs_error =\
            self.packetHandler.ReadPosSpeed(servo_id)

        if scs_comm_result != COMM_SUCCESS:
            scs_comm_result_explain = self.packetHandler.getTxRxResult(scs_comm_result)
            print(self.packetHandler.getTxRxResult(scs_comm_result))
        else:
            #print("[ID:%03d] PresPos:%d PresSpd:%d" % (servo_id, scs_present_position, scs_present_speed))
            pass
        if scs_error != 0:
            scs_servo_stat_err_explain = self.packetHandler.getRxPacketError(scs_error)
            print(scs_servo_stat_err_explain)
        

        return (scs_present_position,scs_present_speed,scs_comm_result,\
                scs_comm_result_explain,scs_servo_stat_err_explain)

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

