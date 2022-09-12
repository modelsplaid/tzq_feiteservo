
from gpiozero import LED, Button
import time
import json
from copy import deepcopy

class ValveController:
    def __init__(self,valve_config_file = "../io_config.json"): 
        self.valve_pinout = []
        self.valve_pin_obj = []
        self.num_valves = 0

        valve_pinout = self.parseValveConfig(valve_config_file)
        self.initValvePins(valve_pinout)
    
    def initValvePins(self,pinout):
        self.valve_pin_obj = deepcopy(pinout)

        for pin in pinout:
            print("pin: " + str(pinout[pin]))   
            ValveIO = LED(pinout[pin])
            self.valve_pin_obj[pin] = ValveIO

    # Turn on valve and pump based on index. 
    # index: 0: right-middle, 1: right-front, 2: left-front, ... 5: right-back 

    def setValveOnOffIndex(self,state = 0,index = 0):
        key_lists = list(self.valve_pin_obj.keys())
        #print("key_lists:"+str(key_lists))
        sel_key = key_lists[index]
        if(state == 1):
            self.valve_pin_obj[sel_key].on()
            print("Turn on: " +str(sel_key)  )
            return True
        if(state == 0):
            self.valve_pin_obj[sel_key].off()
            print("Turn off: " +str(sel_key)  )
            return True         

        return False



           
            
    def parseValveConfig(self,valve_config_file = "../io_config.json"):
        with open(valve_config_file, "r") as fObj:
            valve_config = json.load(fObj)
            print("valve_config:")
            print(valve_config)
            self.valve_pinout = valve_config["valve_pinout"] 
            print("valve_pinout: \n" +str (self.valve_pinout))

        self.num_valves = len(valve_config["valve_pinout"])
        print("num valves: "+str(self.num_valves))
        return self.valve_pinout

    def getNumValves(self):
        return self.num_valves


if __name__ == '__main__':
    valve_ctl = ValveController()

    for j in range(10):
        for i in range(6):
            valve_ctl.setValveOnOffIndex(state = 1, index = i)
            time.sleep(1)

        time.sleep(1)
        for i in range(6):
            valve_ctl.setValveOnOffIndex(state = 0, index = i)
            time.sleep(1)



