import paho.mqtt.client as mqtt
from flask import Flask
import datetime
import json

from flask_mail import Mail
from flask_mail import Message
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

app.config['MAIL_SERVER']=os.getenv("MAIL_SERVER")
app.config['MAIL_PORT'] = os.getenv("MAIL_PORT")
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

pub_topic = "ESP32_01/pub"
sub_topic = "ESP32_01/sub"

# Define MQTT client callbacks
def on_connect(client, userdata, flags, rc, properties=None):
    print("Connected to MQTT broker with result code "+str(rc))
    client.subscribe(sub_topic)

    message = json.dumps({"eventType": "connected", "date_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
    print(f'publish: topic: {pub_topic} %s message: {message}')
    client.publish(pub_topic, payload=message, qos=0, retain=False)

def on_message(client, userdata, message):
    print("Received message on topic "+message.topic+" with payload "+message.payload.decode())
    payload = json.loads(message.payload.decode())

    with app.app_context():
        msg = Message(subject="Notificação de chegada em sala de aula",
                    body=f"O {payload.get('message')} chegou em sala de aula",
                    sender="no-reply@example.com",
                    recipients=["me@example.com"])
        
        mail.send(msg)

# Create MQTT client and connect to broker

client = mqtt.Client(client_id="server_thing",protocol=mqtt.MQTTv5)
client.tls_set(
    ca_certs="AmazonRootCA1.pem",
    certfile="cert.crt",
    keyfile="private.key",
    tls_version=2
)

client.on_connect = on_connect
client.on_message = on_message
client.connect("avlelmwxtr62o-ats.iot.sa-east-1.amazonaws.com", 8883, 60)
# Start MQTT client loop in a separate thread
client.loop_start()


# Define Flask routes
@app.route('/')
def index():
    return 'Hello, world!'

# Run Flask app
if __name__ == '__main__':
    app.run(debug=True)