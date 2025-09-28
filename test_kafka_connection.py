"""
Test Kafka Connection
Quick test to see if Kafka is accessible
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import json

load_dotenv()

def test_kafka_connection():
    """Test if Kafka is running and accessible"""
    bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    topic_name = os.getenv('KAFKA_IOT_TOPIC', 'iot-sensors')
    
    print(f"🔍 Testing Kafka connection...")
    print(f"📡 Bootstrap servers: {bootstrap_servers}")
    print(f"📋 Topic: {topic_name}")
    
    # Test producer
    print(f"\n🧪 Testing Kafka Producer...")
    try:
        producer = KafkaProducer(
            bootstrap_servers=[bootstrap_servers],
            value_serializer=lambda x: json.dumps(x).encode('utf-8'),
            request_timeout_ms=5000,  # 5 second timeout
            api_version=(0, 10, 1)    # Try specific API version
        )
        
        # Send test message
        test_message = {
            'device_name': 'TEST_DEVICE',
            'timestamp': datetime.now().isoformat(),
            'sensors': {
                'current_amps': 10.0,
                'temperature_celsius': 25.0,
                'pressure_bar': 1.0
            }
        }
        
        future = producer.send(topic_name, test_message)
        record_metadata = future.get(timeout=10)
        
        print(f"✅ Producer test successful!")
        print(f"   📊 Sent to partition {record_metadata.partition}")
        print(f"   📊 Offset: {record_metadata.offset}")
        
        producer.close()
        return True
        
    except Exception as e:
        print(f"❌ Producer test failed: {e}")
        print(f"💡 Possible issues:")
        print(f"   - Kafka server not running")
        print(f"   - Wrong bootstrap server address")
        print(f"   - Network connectivity issues")
        print(f"   - Topic doesn't exist")
        return False

def test_kafka_consumer():
    """Test if we can consume from Kafka"""
    bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    topic_name = os.getenv('KAFKA_IOT_TOPIC', 'iot-sensors')
    
    print(f"\n🧪 Testing Kafka Consumer...")
    try:
        consumer = KafkaConsumer(
            topic_name,
            bootstrap_servers=[bootstrap_servers],
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            auto_offset_reset='latest',
            consumer_timeout_ms=5000,  # 5 second timeout
            api_version=(0, 10, 1)
        )
        
        print(f"✅ Consumer created successfully!")
        print(f"   📊 Subscribed to topic: {topic_name}")
        
        consumer.close()
        return True
        
    except Exception as e:
        print(f"❌ Consumer test failed: {e}")
        return False

def check_kafka_status():
    """Check if Kafka is running"""
    import subprocess
    
    print(f"\n🔍 Checking if Kafka processes are running...")
    
    try:
        # Check for Kafka processes on Windows
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq java.exe'], 
                              capture_output=True, text=True)
        
        if 'java.exe' in result.stdout:
            print(f"✅ Java processes found (Kafka likely running)")
            
            # Check for Kafka-specific processes
            if 'kafka' in result.stdout.lower():
                print(f"✅ Kafka processes detected")
            else:
                print(f"⚠️ Java running but no obvious Kafka processes")
        else:
            print(f"❌ No Java processes found")
            print(f"💡 Kafka is typically run with Java")
            
    except Exception as e:
        print(f"⚠️ Could not check processes: {e}")

if __name__ == "__main__":
    print("🔧 Kafka Connection Test")
    print("=" * 40)
    
    check_kafka_status()
    producer_ok = test_kafka_connection()
    consumer_ok = test_kafka_consumer()
    
    print(f"\n📊 Test Results:")
    print(f"   Producer: {'✅ OK' if producer_ok else '❌ FAILED'}")
    print(f"   Consumer: {'✅ OK' if consumer_ok else '❌ FAILED'}")
    
    if producer_ok and consumer_ok:
        print(f"\n🎉 Kafka is working correctly!")
        print(f"✅ You can now run the IoT simulator and data processor")
    else:
        print(f"\n❌ Kafka connection issues detected")
        print(f"💡 Try these steps:")
        print(f"   1. Make sure Kafka server is running")
        print(f"   2. Check if the topic '{os.getenv('KAFKA_IOT_TOPIC', 'iot-sensors')}' exists")
        print(f"   3. Verify bootstrap server address: {os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')}")
        print(f"   4. Check firewall/network settings")
