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
#  Contributors: Daniel Siegel @ Fraunhofer IEM
# *****************************************************************************



#When contributing, please make sure to stick to PEP8 as much as possible.
#https://www.python.org/dev/peps/pep-0008/
from influxdb import InfluxDBClient
import paho.mqtt.client as mqtt
import simplejson

class InfluxAdapter():
    '''Adapter to pipe results from MQTT IDS to InfluxDB for visualization purposes'''
    def __init__(self,BROKER_IP='test.mosquitto.org'):
        self.BROKER_IP = BROKER_IP

        self.client = InfluxDBClient(host='68.183.66.50',port=8086)
        self.client.switch_database('Traces')

        self.mqtt_client = mqtt.Client()
        try:
            self.mqtt_client.connect(self.BROKER_IP)
            self.mqtt_client.subscribe("REFINED")
        except Exception:
            print("Cant establish MQTT connection")
            raise SystemExit(0)
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.loop_forever()

    def on_message(self,client,userdata,msg):
        '''Handles incoming MQTT messages'''
        print("Got new message: {0}".format(str(msg)))
        datadict = simplejson.loads(msg)

        timestamp = datadict['timestamp']
        data = datadict['data']
        processname = datadict['processname']

        datapoint = self.create_json_dict(timestamp,data,processname,'traces')
        self.insert([datapoint])


    def create_json_dict(self,timestamp,data,processname,measurement):
        '''Creates a json style dict as a datapoint to be inserted'''
        tags   = {'processname':processname}
        fields = {'systemcall':data}
        body   = {'measurement':measurement,
                  'tags':tags,
                  'time':timestamp,
                  'fields':fields}
        return body
        

    def insert(self,datapoints):
        '''Takes a list of datapoints created via create_json_dict()
           Inserts these into the InfluxDB.'''
        if self.client.write_points(datapoints) == True:
            print("Inserted for process {0} syscall {1} with time {2}".format(datapoints['processname'],datapoints['systemcall'],datapoints['time']))            
        else:
            print("Something went wrong")

if __name__ == "__main__":
    adapter = InfluxAdapter("test.mosquitto.org")