from flask import Flask, render_template, jsonify
import paho.mqtt.client as mqtt

app = Flask(__name__)

# MQTT Setup
MQTT_BROKER = "broker.hivemq.com"  # Use HiveMQ broker
MQTT_PORT = 1883
MQTT_TOPIC = "raspberrypi/sensor/distance"
mqtt_client = mqtt.Client()

# Variable to store the last received distance
current_distance = None

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT Broker with result code {rc}")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    global current_distance
    try:
        current_distance = float(msg.payload.decode())
        print(f"Received message: {current_distance} cm")
    except Exception as e:
        print(f"Error processing message: {e}")

# Connect to MQTT broker and set callbacks
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_distance', methods=['GET'])
def get_distance():
    if current_distance is not None:
        return jsonify(distance=current_distance)
    else:
        return jsonify({"error": "No data available from Raspberry Pi"}), 500

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
