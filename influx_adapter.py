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
from influxdb import InfluxDBClient
import paho.mqtt.client as mqtt
import simplejson

class InfluxAdapter():
    '''Adapter to pipe results from MQTT IDS to InfluxDB for visualization purposes'''
    def __init__(self):
        self.client = InfluxDBClient(host='68.183.66.50',port=8086)


    def main(self):
        self.client.switch_database('Traces')

    def on_message(self,client,userdata,msg):
        '''Handles incoming MQTT messages'''
        datadict = simplejson.loads(msg)


    def jsonify(data):