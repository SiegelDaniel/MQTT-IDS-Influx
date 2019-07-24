#!/usr/bin/env python3

# *****************************************************************************
#  Copyright (c) 2018 Fraunhofer IEM and others
#
#  This program and the accompanying materials are made available under the
#  terms of the Eclipse Public License 2.0 which is available at
#  http://www.eclipse.org/legal/epl-2.0
#
#  SPDX-License-Identifier: EPL-2.0
#
#  Contributors: Fraunhofer IEM
# *****************************************************************************


#When contributing, please make sure to stick to PEP8 as much as possible.
#https://www.python.org/dev/peps/pep-0008/
import simplejson
import paho.mqtt.client as mqtt

class LUTCreator(object):

    def __init__(self,BROKER_IP):
        self.BROKER_IP = BROKER_IP
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_log     = self.on_log
        

        self.LUT  = {}

        self.client.connect(BROKER_IP)
        self.client.loop_forever()

    def on_connect(self,client,userdata,flags,rc):
        """Consists of actions to take when the connection is established."""
        print("Subscribing to REFINED")
        self.client.subscribe("REFINED") 

    def on_log(self,client, userdata, level, buf):
        """Uses the built-in logger to output errors and events of interest"""
        print("log: ",buf)

    def on_message(self,client,userdata,msg):
        '''Handles incoming MQTT messages'''
        datadict = simplejson.loads(str(msg.payload,'utf-8'))
        trace = datadict['data']

        try:
            temp = self.LUT[trace]
            temp += 1 
            self.LUT[trace] = temp
        except KeyError:
            self.LUT[trace] = 1

        with open('data.json', 'w') as f:
            simplejson.dump(self.LUT, f)

if __name__ == "__main__":
    try:
        LUT = LUTCreator("test.mosquitto.org")
    except Exception as e:
        print(str(e))