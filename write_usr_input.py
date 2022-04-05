# todo: write to speified servo by usr input 
#!/usr/bin/env python
#
# *********     Gen Write Example      *********
#
#
# Available SCServo model on this example : All models using Protocol SCS
# This example is tested with a SCServo(STS/SMS/SCS), and an URT
# Be sure that SCServo(STS/SMS/SCS) properties are already set as %% ID : 1 / Baudnum : 6 (Baudrate : 1000000)
#

import os
import json

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

from scservo_sdk import *                    # Uses SCServo SDK library

class servo_controller:
    
    def __init__(self):    
        self.parseServoConfig()
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
            self.SCS_ID = servo_config['serial_params']['SCS_ID']
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

    def setAcc(self):
        # Write SCServo acc
        scs_comm_result, scs_error = self.packetHandler.write1ByteTxRx(\
            self.portHandler, self.SCS_ID, self.ADDR_SCS_GOAL_ACC, self.SCS_MOVING_ACC)
        if scs_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(scs_comm_result))
        elif scs_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(scs_error))

    def setSpeed(self,speed_val=0):

        # Write SCServo speed
        scs_comm_result, scs_error = self.packetHandler.write2ByteTxRx\
            (self.portHandler, self.SCS_ID, self.ADDR_SCS_GOAL_SPEED, speed_val)
        if scs_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(scs_comm_result))
        elif scs_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(scs_error))

    def setPosition(self,position_val=0):

            # Write SCServo goal position
            scs_comm_result, scs_error = \
                self.packetHandler.write2ByteTxRx\
                (self.portHandler, self.SCS_ID, self.ADDR_SCS_GOAL_POSITION,position_val)
            if scs_comm_result != COMM_SUCCESS:
                print("%s" % self.packetHandler.getTxRxResult(scs_comm_result))
            elif scs_error != 0:
                print("%s" % self.packetHandler.getRxPacketError(scs_error))

    def getPoseSpeed(self):
        
        scs_present_position_speed, scs_comm_result, scs_error =\
            self.packetHandler.read4ByteTxRx(\
            self.portHandler, self.SCS_ID, self.ADDR_SCS_PRESENT_POSITION)
        if scs_comm_result != COMM_SUCCESS:
            print(self.packetHandler.getTxRxResult(scs_comm_result))
        elif scs_error != 0:
            print(self.packetHandler.getRxPacketError(scs_error))

        scs_present_position = SCS_LOWORD(scs_present_position_speed)
        scs_present_speed = SCS_HIWORD(scs_present_position_speed)
        print("[ID:%03d] PresPos:%03d PresSpd:%03d" 
              % (self.SCS_ID, scs_present_position, SCS_TOHOST(scs_present_speed, 15)))

    def deactivateTorque(self):

        scs_comm_result, scs_error = self.packetHandler.write1ByteTxRx(\
            self.portHandler, self.SCS_ID, self.ADDR_SCS_TORQUE_ENABLE, 0)
        if scs_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(scs_comm_result))
        elif scs_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(scs_error))

    def closePort(self):
        # Close port
        self.portHandler.closePort()



if __name__ == '__main__':
    servoCtl = servo_controller()

    
    while (True):
        user_msg = input("Input servo position: (or press ESC to quit!)")
        servo_speed = int(user_msg[0])*200            
        servo_pose = int(user_msg[1])*1000            
        if user_msg == chr(0x1b):
            break            

        print("User given speed: "+str(servo_speed))
        print("User given position: "+str(servo_pose))

        servoCtl.setPosition(servo_pose)
        servoCtl.setSpeed(servo_speed)
        servoCtl.getPoseSpeed()