## Description: 

    This project is to communicate feite scs serial servos and turn on/off the pumps and valves . 
    It can set serovs' position,speed,and torque.  
    It receives present position,speed,and torque value in a fixed frequency.

## Program working flow: 
    It has two queues. One is for sending data, the other is for receiving.
    The class MultiServoController() will create a thread, and keep reading 
    servos' position, speed, and torque to receive queue. If the send queue 
    is not empty, the thread will pop out data from send queue and send to servos. 

## How to use: 
    Dependancy: 
        Serial driver, python3, ubuntu or raspberrypi 
    How to run:
        python3 test_main.py

## Pinout:

### Serial port pinout:
    This project is using ttyAMA1 as default serial port. 
    The pins for rpi4's ttyAMA1 is:
    ttyAMA1 Tx : GPIO 0
    ttyAMA1 Rx : GPIO 1 
    By default rpi4 doest not set GPIO 0 and 1 as serial port, to 
    change it as serial port, look below "How to change rpi4 serial port"
    Serial ports can be changed in servo_config.json

### Valve & pump pinout:

    There are 3 driver modules, each controls two pumps and valves. 
    Each pair of pump and valve share the same output pin on driver modules. 

    Driver modules' output 1,output 3 connect the ground of pump and valve pair 
    Driver modules' output 2,output 4 connect the positive of pump and valve pair

    Driver modules' input 1, input 3 does not connet to rpi, just leave it there. 
    Driver modules' input 2, input 4 connect to rpi's IO pin.  

    IO_19--->Driver module 1 ,input 1 --->output 1 ---> Left front pump and valve pair 
    IO_16--->Driver module 1 ,input 3 --->output 3 ---> Right front pump and valve pair

    IO_06--->Driver module 2 ,input 1 --->output 1 ---> Left back pump and valve pair 
    IO_12--->Driver module 2 ,input 3 --->output 3 ---> Left middle pump and valve pair

    IO_18--->Driver module 2 ,input 1 --->output 1 ---> Right middle pump and valve pair 
    IO_17--->Driver module 2 ,input 3 --->output 3 ---> Right back pump and valve pair

    These pinouts can be changed in io_config.json

### How to change rpi4 serial port: 
    There are four new overlays for hardware serial ports - uart2 to uart5. 
    After loading they will be available as /dev/ttyAMA1-4. 
    To activate one of the additional hardware serial ports, 
    add the following to /boot/config.txt:
        dtoverlay=uart2
    To create a serial port with flow control, use:
        dtoverlay=uart2,ctsrts
    The port will then be available via /dev/ttyAMA1

    To see the GPIO pin allocation for a uart via 
    the command-line use: dtoverlay -h uart2
    (https://forums.raspberrypi.com/viewtopic.php?t=244528)


### How to print out gpio layouts:
    raspi-gpio get 0-1
    pinout

## Inter porcess communication protocols

### Servos

    "device_id": 1,
    "send_servo_valid": 
            false: means below send_* value is not valid

    "send_servo_pos_val":
            in steps 

    "send_servo_speed_val":
            steps/sec 

    "send_servo_torque_val": 
            no unit yet

    "send_servo_commu_result":
            possible error for send pose_speed: 
                "[TxRxResult] Communication success!"
                "[TxRxResult] Port is in use!"
                "[TxRxResult] Failed transmit instruction packet!"
                "[TxRxResult] Failed get status packet from device!"
                "[TxRxResult] Incorrect instruction packet!"
                "[TxRxResult] Now receiving status packet!"
                "[TxRxResult] There is no status packet!"
                "[TxRxResult] Incorrect status packet!"
                "[TxRxResult] Protocol does not support this function!"

    "send_servo_status_error":
            possible error for send pose_speed:
                "[ServoStatus] Input voltage error!"
                "[ServoStatus] Angle sen error!"
                "[ServoStatus] Overheat error!"
                "[ServoStatus] OverEle error!"
                "[ServoStatus] Overload error!"

    "recv_servo_valid": false,      \
    "recv_servo_pos_val": 99999,    |
    "recv_servo_torque_val": 99999, \ same 
    "recv_servo_speed_val": 99999,  / as above
    "recv_servo_commu_result": "",  |  
    "recv_servo_status_error": "",  /
    "time_stamp":  In seconds, systme time 

### Valves and pumps

    "valve_pump_id"     : From 0 (right-middle leg) to 6(right-back leg)
                            The ID is in counter-clockwise order

    "valve_pump_name"   : "right-middle-valve-pump" ... "right-back-valve-pump"

    "pump_status"       : 0: Pump is leaking air(Sucktion cup is not vacum )  , 
                          1: Pump is sealed well

    "turn_onoff_val_pump" : 0: Turn off valve and pump,
                            1: Turn on valve and pump 
                            2: No action 

    "time_stamp"        : In seconds, systme time
    



## References: 
    https://gitee.com/ftservo/SCServoSDK            
    https://forums.raspberrypi.com/viewtopic.php?t=244528
    
 
 
 
 
 
 
 
