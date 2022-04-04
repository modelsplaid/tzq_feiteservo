import json

dic_serial_params = dict(\
                    SCS_ID = 1,\
                    BAUDRATE = 1000000,\
                    DEVICENAME = '/dev/ttyUSB0'
                    )

dic_net_params = dict(\
                IP = "",
                PORT = 20000
                )

dic_servo_params = dict(\
                # SCServo will rotate between this value
                SCS_MINIMUM_POSITION_VALUE  = 2000,\
                # and this value 
                SCS_MAXIMUM_POSITION_VALUE  = 3000,\
                SCS_MOVING_STATUS_THRESHOLD = 20,\
                # SCServo moving status threshold
                SCS_MOVING_SPEED            = 500,\
                # SCServo moving speed
                SCS_MOVING_ACC              = 0,\
                # SCServo moving acc
                protocol_end                = 0
                # SCServo bit end(STS/SMS=0, SCS=1)
                )

dic_servo_control_table = dict(\
                        ADDR_SCS_TORQUE_ENABLE     = 40,\
                        ADDR_SCS_GOAL_ACC          = 41,\
                        ADDR_SCS_GOAL_POSITION     = 42,\
                        ADDR_SCS_GOAL_SPEED        = 46,\
                        ADDR_SCS_PRESENT_POSITION  = 56    
    )

servo_config =dict(\
                serial_params=dic_serial_params,\
                net_params=dic_net_params,\
                servo_params=dic_servo_params,\
                servo_control_table=dic_servo_control_table           
                )



# Serializing json 
json_object = json.dumps(servo_config, indent = 4)
# Writing to sample.json
with open("servo_config.json", "w") as outfile:
    outfile.write(json_object)