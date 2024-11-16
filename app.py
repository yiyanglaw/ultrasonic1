import RPi.GPIO as GPIO
import time
import paho.mqtt.client as mqtt
from flask import Flask, render_template, jsonify
import os

# Flask app setup, specify current directory for templates
app = Flask(__name__, template_folder=os.getcwd())

# MQTT Setup
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "raspberrypi/servo/control"

# Ultrasonic Sensor Pins
TRIG = 23
ECHO = 24

# Servo Pin (GPIO 17 for example)
SERVO_PIN = 17

# GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# Initialize PWM for Servo
servo = GPIO.PWM(SERVO_PIN, 50)  # 50Hz
servo.start(0)

# MQTT Client Setup
mqtt_client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT Broker with result code {rc}")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    message = msg.payload.decode()
    print(f"Message received: {message}")
    if message == "open":
        # Move servo to open position
        servo.ChangeDutyCycle(7)
        time.sleep(1)
        servo.ChangeDutyCycle(0)
    elif message == "close":
        # Move servo to close position
        servo.ChangeDutyCycle(3)
        time.sleep(1)
        servo.ChangeDutyCycle(0)

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()

# Function to get ultrasonic sensor distance
def get_distance():
    GPIO.output(TRIG, GPIO.LOW)
    time.sleep(0.5)
    
    GPIO.output(TRIG, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(TRIG, GPIO.LOW)
    
    while GPIO.input(ECHO) == GPIO.LOW:
        pulse_start = time.time()
    
    while GPIO.input(ECHO) == GPIO.HIGH:
        pulse_end = time.time()
    
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150  # Distance in cm
    distance = round(distance, 2)
    
    return distance

@app.route('/')
def index():
    distance = get_distance()
    return render_template('index.html', distance=distance)

@app.route('/control_servo/<action>')
def control_servo(action):
    if action == 'open':
        mqtt_client.publish(MQTT_TOPIC, "open")
    elif action == 'close':
        mqtt_client.publish(MQTT_TOPIC, "close")
    return jsonify({'status': 'success', 'action': action})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
