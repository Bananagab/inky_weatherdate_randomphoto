from paho.mqtt import client as mqtt_client
import time
import os
import random
from dotenv import load_dotenv
import sys
import signal
from PIL import Image
from inky.auto import auto
import getweatherdate

inky = auto(ask_user=False, verbose=False)
saturation = 0.5

load_dotenv()

broker = os.getenv("MQTT_BROKER")
port = int(os.getenv("MQTT_PORT"))
topic = os.getenv("MQTT_TOPIC")
username = os.getenv("MQTT_USERNAME")
password = os.getenv("MQTT_PASSWORD")
client_id = f'cadre-{random.randint(0, 1000000000)}'

def get_random_file_path(folder_path):
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    if files:
        return os.path.join(folder_path, random.choice(files))
    else:
        return None

def set_image():
    image = getweatherdate.get_weather(get_random_file_path('/home/bananapi/inky/pic/pics'))
    inky.set_image(image, saturation=saturation)
    inky.show()

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(topic)
    elif rc == 5:
        print("Failed to connect, return code Not authorized")
    else:
        print(f"Failed to connect, return code {rc}\n")
        
def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8')
    if payload == 'random':
        set_image()
    else:
        return
    
def main():
    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2, client_id=client_id, protocol=mqtt_client.MQTTv311, transport="tcp")
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.on_message = on_message
    
        
    def signal_handler(sig, frame):
        print('Exiting...')
        client.disconnect()
        sys.exit(0)
    
    
    print(f"Connecting to {broker}:{port} with client_id {client_id}")
    print(f"Using username: {username} and password: {password}")
    print(f"Client ID: {client_id}")
    client.connect(broker, port)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    client.loop_forever()

if __name__ == "__main__":
    main()