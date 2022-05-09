## Description: 

    This project is to communicate feite scs serial servos. 
    It can set serovs' position,speed,and torque.  
    It receive present position,speed,and torque value in a fixed frequency.
    It also supports multiple servers, just add a new item in servo_commu.json.    


## Program working flow: 
    It has two queues. One is send queue, the other is receive queue.
    The class MultiServoController() will create a thread, and keep reading 
    servos' position, speed, and torque to receive queue. If the send queue 
    is not empty, the thread will pop out data from send queue and send to servos. 

## How to use: 
    Dependancy: 
        Serial driver, python3, ubuntu or raspberrypi 
    How to run:
        python3 test_main.py

## How to decrease/increse servos: 
    Edit servo_commu.json 

## How to change rpi4 serial port: 
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

## How to print out gpio layouts:
    raspi-gpio get 0-1
    pinout



## References: 
    https://gitee.com/ftservo/SCServoSDK            
    https://forums.raspberrypi.com/viewtopic.php?t=244528
 
 
 
 
 
 
 
