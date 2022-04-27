Description: 

    This project is to communicate feite scs serial servos. 
    It can set serovs' position,speed,and torque.  
    It receive present position,speed,and torque value in a fixed frequency.
    It also supports multiple servers, just add a new item in servo_commu.json.    


Program working flow: 
    It has two queues. One is send queue, the other is receive queue.
    The class MultiServoController() will create a thread, and keep reading 
    servos' position, speed, and torque to receive queue. If the send queue 
    is not empty, the thread will pop out data from send queue and send to servos. 

How to use: 
    Dependancy: 
        Serial driver, python3, ubuntu or raspberrypi 
    How to run:
        python3 test_main.py

How to decrease/increse servos: 
    Edit servo_commu.json 

References: 
    https://gitee.com/ftservo/SCServoSDK            

 
 
 
 
 
 
 
