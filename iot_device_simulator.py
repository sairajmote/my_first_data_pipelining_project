"""
IoT Device Simulator
This script creates fake IoT devices that generate sensor readings
Think of it like having 5 energy meters in different rooms of a factory
"""

import random
import time
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from kafka import KafkaProducer
from kafka.errors import KafkaError

# Load environment variables from .env file (if it exists)
load_dotenv()

class KafkaDataSender:
    """
    This class handles sending data to Kafka
    Think of it as a "mail service" that delivers messages to Kafka
    """
    
    def __init__(self):
        # Get Kafka settings from environment variables
        self.bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        self.topic_name = os.getenv('KAFKA_IOT_TOPIC', 'iot-sensors')
        
        # Create Kafka producer (the thing that sends messages)
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=[self.bootstrap_servers],
                # Convert Python objects to JSON format for sending
                value_serializer=lambda x: json.dumps(x).encode('utf-8'),
                # Add some reliability settings
                acks='all',  # Wait for confirmation that message was received
                retries=3,   # Try 3 times if sending fails
                max_in_flight_requests_per_connection=1  # Send one message at a time
            )
            print(f"✅ Connected to Kafka at {self.bootstrap_servers}")
            print(f"📡 Will send data to topic: {self.topic_name}")
        except Exception as e:
            print(f"❌ Failed to connect to Kafka: {e}")
            print(f"💡 Make sure Kafka is running on {self.bootstrap_servers}")
            self.producer = None
    
    def send_sensor_data(self, sensor_data):
        """
        Send sensor data to Kafka topic
        Like putting a letter in the mailbox
        """
        if self.producer is None:
            print("❌ Cannot send data - Kafka producer not available")
            return False
        
        try:
            # Send the data to Kafka topic
            future = self.producer.send(self.topic_name, sensor_data)
            
            # Wait a bit to see if it was sent successfully
            record_metadata = future.get(timeout=10)
            
            # Success! The data was sent to Kafka
            return True
            
        except KafkaError as e:
            print(f"❌ Failed to send data to Kafka: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error sending to Kafka: {e}")
            return False
    
    def close(self):
        """
        Close the Kafka connection properly
        Like closing the mailbox when done
        """
        if self.producer:
            self.producer.close()
            print("📪 Kafka connection closed")

class IoTDevice:
    """
    This class represents one IoT device (like one energy meter)
    Each device has a unique ID and generates sensor readings
    """
    
    def __init__(self, device_id):
        # Give each device a unique name like "EnergyDevice_001"
        self.device_id = device_id
        self.device_name = f"{os.getenv('DEVICE_NAME_PREFIX', 'EnergyDevice')}_{device_id:03d}"
        
        # Get the ranges for generating random sensor values from environment variables
        # If not set in .env, use default values
        self.current_min = float(os.getenv('CURRENT_MIN', 5.0))
        self.current_max = float(os.getenv('CURRENT_MAX', 20.0))
        self.temp_min = float(os.getenv('TEMPERATURE_MIN', 20.0))
        self.temp_max = float(os.getenv('TEMPERATURE_MAX', 90.0))
        self.pressure_min = float(os.getenv('PRESSURE_MIN', 1.0))
        self.pressure_max = float(os.getenv('PRESSURE_MAX', 3.0))
        
        print(f"✅ Created device: {self.device_name}")
    
    def generate_sensor_reading(self):
        """
        This function creates fake sensor data
        Like reading the actual meters in a real factory
        """
        
        # Generate random values within the specified ranges
        current = round(random.uniform(self.current_min, self.current_max), 2)
        temperature = round(random.uniform(self.temp_min, self.temp_max), 2)
        pressure = round(random.uniform(self.pressure_min, self.pressure_max), 2)
        
        # Create a timestamp for when this reading was taken
        timestamp = datetime.now().isoformat()
        
        # Package all the data into a dictionary (like a JSON message)
        sensor_data = {
            "device_id": self.device_id,
            "device_name": self.device_name,
            "timestamp": timestamp,
            "sensors": {
                "current_amps": current,
                "temperature_celsius": temperature,
                "pressure_bar": pressure
            }
        }
        
        return sensor_data
    

def main():
    """
    Main function - this is where the program starts
    Creates multiple devices and makes them generate data continuously
    Now sends data to Kafka instead of just printing!
    """
    
    print("🚀 Starting IoT Device Simulator with Kafka Integration...")
    print("=" * 60)
    
    # Get configuration from environment variables
    device_count = int(os.getenv('DEVICE_COUNT', 5))
    interval = int(os.getenv('SIMULATION_INTERVAL', 3))
    
    print(f"📱 Creating {device_count} simulated devices...")
    print(f"⏰ Sending data every {interval} seconds...")
    print("=" * 60)
    
    # Create Kafka data sender (our connection to Kafka)
    kafka_sender = KafkaDataSender()
    
    # Create a list of IoT devices (like having multiple energy meters)
    devices = []
    for i in range(1, device_count + 1):
        device = IoTDevice(i)
        devices.append(device)
    
    print(f"\n🎯 All devices created! Starting data generation...")
    print("Press Ctrl+C to stop the simulation\n")
    
    try:
        # Keep running forever (until user stops it)
        while True:
            print(f"\n📊 Data Collection Round - {datetime.now().strftime('%H:%M:%S')}")
            print("-" * 60)
            
            successful_sends = 0
            failed_sends = 0
            
            # Each device generates and sends its sensor reading
            for device in devices:
                # Generate fake sensor data
                sensor_reading = device.generate_sensor_reading()
                
                # Send data to Kafka - this is our only job!
                kafka_success = kafka_sender.send_sensor_data(sensor_reading)
                
                if kafka_success:
                    successful_sends += 1
                else:
                    failed_sends += 1
                
                # Display the data in a nice format (but less verbose with 100 devices)
                print(f"📡 {sensor_reading['device_name']}: "
                      f"Current={sensor_reading['sensors']['current_amps']}A, "
                      f"Temp={sensor_reading['sensors']['temperature_celsius']}°C, "
                      f"Pressure={sensor_reading['sensors']['pressure_bar']}bar "
                      f"{'✅' if kafka_success else '❌'}")
                
                # No alerts here - that's the data processor's job!
            
            # Summary of this round
            print(f"\n📈 Round Summary: {successful_sends} sent successfully, {failed_sends} failed")
            if kafka_sender.producer:
                print(f"📡 Data sent to Kafka topic: {kafka_sender.topic_name}")
            
            # Wait before generating the next round of data
            time.sleep(interval)
            
    except KeyboardInterrupt:
        # This happens when user presses Ctrl+C
        print("\n\n🛑 Simulation stopped by user")
        kafka_sender.close()  # Close Kafka connection properly
        print("👋 Goodbye!")

# This is Python's way of saying "run the main function when this file is executed"
if __name__ == "__main__":
    main()
