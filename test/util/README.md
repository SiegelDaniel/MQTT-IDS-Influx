

## Simulating an attack and testing the IDS
***attack.py*** is a Python program that creates a specific deterministic behaviour in terms of Systemcalls.
  
This file is meant to be run in *learning mode* to train a demo-IDS. Learning mode is enabled by default and means that no messages are received on the **MQTT** topic "`**ATTACK**`" at the given **MQTT** broker.   

To simulate an attack or anomalous behaviour, just send a message on the topic "**`ATTACK`**" via **MQTT** to the broker at `test.mosquitto.org`.  

The program listens to this topic and starts I/O-heavy operations shortly after receiving a message.  
This will result in systemcall traces that are very different than the training behaviour and will lead the IDS to signal an alarm. 

