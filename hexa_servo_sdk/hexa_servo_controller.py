
import sys, tty, termios
import os
import json
from .port_handler import * 
from .packet_handler import *

fd = sys.stdin.fileno()
old_settings = termios.tcgetattr(fd)

def getch():
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


class servo_controller:
    
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

            #2. parse net params 
            self.IP = servo_config['net_params']['IP']
            self.PORT = servo_config['net_params']['PORT']
            
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


