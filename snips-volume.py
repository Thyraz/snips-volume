#!/usr/bin/env python3
import json
import os
import string
import re

import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import toml

import alsaaudio

# sudo apt-get install libasound2-dev, sudo pip3 install pyalsaaudio

# Subscribe topics
def on_connect(client, userdata, flags, rc):
    print("MQTT connected")
    client.subscribe("hermes/sound/setvolume")
    client.subscribe("hermes/sound/getvolume")


# Get volume from alsa
def get_volume():
    mixer = alsaaudio.Mixer()
    volume = mixer.getvolume()
    # Extract integer value from List of longs
    volume = int(vol[0])

    return volume


# Set volume to alsa
def set_volume(volume):
    mixer = alsaaudio.Mixer()
    volume = mixer.getvolume()
    # Extract integer value from List of longs
    volume = int(vol[0])


# Received set message from MQTT
def on_set(client, userdata, msg):
    # Parse JSON from MQTT
    data = json.loads(msg.payload.decode())
    target_id = data['siteId']
    volume = data['volume']

    if target_id == site_id:
        # Set volume
        set_volume(volume)


# Received get message from MQTT
def on_get(client, userdata, msg):
    # Parse JSON from MQTT
    data = json.loads(msg.payload.decode())
    target_id = data['siteId']

    if target_id == site_id:
        # Get volume
        volume = get_volume()

        # Send answer to mqtt
        msgs = [
            {
                "topic": "hermes/sound/volume",
                "payload": json.dumps({"volume": volume, "siteId": site_id}),
            },
        ]
        publish.multiple(msgs, hostname=mqtt_host, port=mqtt_port)


# Create client and callback
client = mqtt.Client()
client.on_connect = on_connect
client.message_callback_add("hermes/sound/setvolume", on_set)
client.message_callback_add("hermes/sound/getvolume", on_get)

# Read MQTT connection info from the central snips config.
snips_config = toml.loads(open("/etc/snips.toml").read())
mqtt_server = snips_config.get("snips-common", {}).get("mqtt")

if mqtt_server is None:
    mqtt_server = "localhost:1883"

mqtt_host, mqtt_port = mqtt_server.split(":")
mqtt_port = int(mqtt_port)
client.connect(mqtt_host, mqtt_port, 60)

# Read siteId from the central snips config.
site_id = snips_config.get("snips-audio-server", {}).get("bind")

if site_id is None:
    site_id = "default@mqtt"

site_id = site_id.split("@")[0]

client.loop_forever()
