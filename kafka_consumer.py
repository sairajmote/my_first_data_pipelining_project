"""
Kafka Consumer
This script reads sensor data from Kafka topic
Think of it as a "mailbox reader" that gets messages and displays them
"""

import json
import os
from datetime import datetime
from dotenv import load_dotenv
from kafka import KafkaConsumer
from kafka.errors import KafkaError

# Load environment variables from .env file
load_dotenv()

class SimpleKafkaConsumer:
    """
    Simple Kafka Consumer that just reads and displays messages
    No alert processing - just pure message consumption
    """
    
    def __init__(self):
        # Get Kafka settings from environment variables
        self.bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        self.topic_name = os.getenv('KAFKA_IOT_TOPIC', 'iot-sensors')
        self.group_id = 'simple-consumer-group'
        
        # Create Kafka consumer (the thing that reads messages)
        try:
            self.consumer = KafkaConsumer(
                self.topic_name,
                bootstrap_servers=[self.bootstrap_servers],
                group_id=self.group_id,
                # Convert JSON messages back to Python objects
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                # Start reading from the latest messages
                auto_offset_reset='latest',
                # Commit offsets automatically
                enable_auto_commit=True,
                auto_commit_interval_ms=1000
            )
            print(f"✅ Kafka Consumer connected to {self.bootstrap_servers}")
            print(f"📡 Listening to topic: {self.topic_name}")
            print(f"👥 Consumer group: {self.group_id}")
        except Exception as e:
            print(f"❌ Failed to connect to Kafka: {e}")
            print(f"💡 Make sure Kafka is running on {self.bootstrap_servers}")
            self.consumer = None
    
    def start_consuming(self):
        """
        Start consuming messages from Kafka
        Just reads and displays - no processing
        """
        
        if self.consumer is None:
            print("❌ Cannot start consuming - Kafka consumer not available")
            return
        
        print(f"\n🎯 Starting message consumption...")
        print("Press Ctrl+C to stop consuming\n")
        
        try:
            message_count = 0
            
            # Keep reading messages forever
            for message in self.consumer:
                message_count += 1
                
                try:
                    # Get the sensor data from the message
                    sensor_data = message.value
                    
                    # Display the message content
                    device_name = sensor_data.get('device_name', 'Unknown')
                    timestamp = sensor_data.get('timestamp', 'No timestamp')
                    sensors = sensor_data.get('sensors', {})
                    
                    print(f"📨 Message #{message_count} - {datetime.now().strftime('%H:%M:%S')}")
                    print(f"   Device: {device_name}")
                    print(f"   Timestamp: {timestamp}")
                    print(f"   Current: {sensors.get('current_amps', 0)}A")
                    print(f"   Temperature: {sensors.get('temperature_celsius', 0)}°C")
                    print(f"   Pressure: {sensors.get('pressure_bar', 0)} bar")
                    print("-" * 50)
                    
                    # Print summary every 50 messages
                    if message_count % 50 == 0:
                        print(f"\n📊 Consumed {message_count} messages so far...\n")
                
                except Exception as e:
                    print(f"❌ Error processing message: {e}")
                    continue
        
        except KeyboardInterrupt:
            print("\n\n🛑 Consumer stopped by user")
            print(f"📈 Total messages consumed: {message_count}")
            print("👋 Goodbye!")
        
        finally:
            if self.consumer:
                self.consumer.close()
                print("📪 Kafka consumer connection closed")

def main():
    """
    Main function - starts the Kafka consumer
    """
    
    print("📡 Starting Simple Kafka Consumer...")
    print("=" * 50)
    
    # Create and start the Kafka consumer
    consumer = SimpleKafkaConsumer()
    consumer.start_consuming()

# This runs when the script is executed
if __name__ == "__main__":
    main()
