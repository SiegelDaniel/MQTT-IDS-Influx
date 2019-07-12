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
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_connect = self.on_connect
        try:
            self.mqtt_client.connect(self.BROKER_IP)
            
        except Exception:
            print("Cant establish MQTT connection")
            raise SystemExit(0)
        
        self.mqtt_client.loop_forever()

    def on_message(self,client,userdata,msg):
        '''Handles incoming MQTT messages'''
        if msg.topic == 'REFINED':
            self.handle_insert(msg)
        elif msg.topic == 'ANOMALY':
            self.handle_anomaly(msg)

    def handle_insert(self,msg):
        '''A handler for messages which were received on the topic REFINED'''
        print("Got new message on REFINED: {0}".format(str(msg)))
        datadict = simplejson.loads(str(msg.payload,'utf-8'))

        data = datadict['data']
        processname = datadict['processname']

        datapoint = self.create_json_dict(data,processname,'traces')
        try:
            self.insert(datapoint)
        except Exception as e:
            print(str(e))

    def handle_anomaly(self,msg):
        '''A handler for messages which were received on the topic ANOMALY'''
        print("Got new message on ANOMALY: {0}".format(str(msg)))
        datadict = simplejson.loads(str(msg.payload,'utf-8'))

        anomalous_data = datadict['trace']
        processname = datadict['processname']

        datapoint = self.create_json_dict(anomalous_data,processname,'anomalies')
        try:
            self.insert(datapoint)
        except Exception as e:
            print(str(e))


    def create_json_dict(self,data,processname,measurement):
        '''Creates a json style dict as a datapoint to be inserted'''
        points = [{
                "measurement":measurement,
                "tags": {
                    "processname": processname
                },
                "fields":
                {
                    "systemcall": data
                }
            }]
        return points
        
    def on_connect(self,client,userdata,flags,rc):
        print("Subscribing to REFINED")
        self.mqtt_client.subscribe("REFINED") 
        self.mqtt_client.subscribe("ANOMALY")

    def insert(self,datapoints):
        '''Takes a list of datapoints created via create_json_dict()
           Inserts these into the InfluxDB.'''
        try:
            print(type(datapoints))
            print(datapoints)
            if self.client.write_points(datapoints,protocol='json') == True:
                print("Success")           
            else:
                print("Something went wrong")
        except Exception as e:
            print("Exception of type {0} in insert. Msg: {1}".format(type(e),str(e)))

if __name__ == "__main__":
    adapter = InfluxAdapter("test.mosquitto.org")