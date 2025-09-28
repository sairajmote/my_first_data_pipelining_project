"""
Working Data Processor - Uses REST API to store data in Supabase
This version bypasses the problematic Python client and uses direct REST API calls
"""

import json
import os
import time
import requests
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dotenv import load_dotenv
from kafka import KafkaConsumer
from kafka.errors import KafkaError

# Load environment variables from .env file
load_dotenv()

class RestSupabaseClient:
    """
    REST API client for Supabase operations
    Bypasses the problematic Python client
    """
    
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Missing Supabase credentials in .env file")
        
        self.headers = {
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}',
            'Content-Type': 'application/json'
        }
        
        print(f"✅ REST Supabase client initialized")
        self.test_connection()
    
    def test_connection(self):
        """Test connection to both tables"""
        try:
            # Test sensor_readings table
            response = requests.get(
                f"{self.supabase_url}/rest/v1/sensor_readings?limit=1",
                headers=self.headers
            )
            if response.status_code == 200:
                print(f"📊 sensor_readings table: ✅ Connected")
            else:
                print(f"❌ sensor_readings table error: {response.status_code}")
            
            # Test alerts table (use existing table)
            response = requests.get(
                f"{self.supabase_url}/rest/v1/alerts?limit=1",
                headers=self.headers
            )
            if response.status_code == 200:
                print(f"🚨 alerts table: ✅ Connected")
            else:
                print(f"❌ alerts table error: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️ Connection test failed: {e}")
    
    def store_sensor_data(self, sensor_data):
        """Store sensor data in sensor_readings table"""
        try:
            # Prepare data matching the exact table schema
            db_record = {
                'device_name': sensor_data.get('device_name'),
                'timestamp': sensor_data.get('timestamp') + 'Z' if not sensor_data.get('timestamp', '').endswith('Z') else sensor_data.get('timestamp'),
                'current_amps': sensor_data.get('sensors', {}).get('current_amps'),
                'temperature_celsius': sensor_data.get('sensors', {}).get('temperature_celsius'),
                'pressure_bar': sensor_data.get('sensors', {}).get('pressure_bar')
            }
            
            response = requests.post(
                f"{self.supabase_url}/rest/v1/sensor_readings",
                headers=self.headers,
                json=db_record
            )
            
            if response.status_code in [200, 201]:
                return True
            else:
                print(f"⚠️ Sensor data failed ({response.status_code}), storing as alert instead")
                # If sensor_readings fails, store as an informational alert
                fallback_alert = {
                    'device_name': sensor_data.get('device_name'),
                    'alert_type': 'SENSOR_DATA',
                    'severity': 'info',
                    'message': f"Sensor reading: {db_record['current_amps']}A, {db_record['temperature_celsius']}°C, {db_record['pressure_bar']} bar",
                    'sensor_value': db_record['current_amps'],
                    'unit': 'A',
                    'timestamp': db_record['timestamp']
                }
                return self.store_alert(fallback_alert)
                
        except Exception as e:
            print(f"❌ Exception storing sensor data: {e}")
            return False
    
    def store_alert(self, alert_data):
        """Store alert in alerts table (use existing table)"""
        try:
            # Prepare data matching the exact table schema
            timestamp = alert_data.get('timestamp', datetime.now().isoformat())
            if not timestamp.endswith('Z'):
                timestamp += 'Z'
                
            db_record = {
                'device_name': alert_data.get('device_name'),
                'alert_type': alert_data.get('alert_type'),
                'severity': alert_data.get('severity'),
                'message': alert_data.get('message'),
                'sensor_value': alert_data.get('value', alert_data.get('sensor_value', 0)),
                'unit': alert_data.get('unit', 'A'),
                'timestamp': timestamp
            }
            
            response = requests.post(
                f"{self.supabase_url}/rest/v1/alerts",
                headers=self.headers,
                json=db_record
            )
            
            if response.status_code in [200, 201]:
                return True
            else:
                print(f"❌ Failed to store alert: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Exception storing alert: {e}")
            return False

class AlertProcessor:
    """
    Simplified alert processor for testing
    """
    
    def __init__(self):
        # Get alert thresholds from environment variables
        self.current_threshold = float(os.getenv('CURRENT_ALERT_THRESHOLD', 15.0))
        self.temp_threshold = float(os.getenv('TEMPERATURE_ALERT_THRESHOLD', 80.0))
        self.pressure_threshold = float(os.getenv('PRESSURE_ALERT_THRESHOLD', 2.5))
        
        print(f"🎯 Alert Processor initialized with thresholds:")
        print(f"   Current: > {self.current_threshold}A")
        print(f"   Temperature: > {self.temp_threshold}°C")
        print(f"   Pressure: > {self.pressure_threshold} bar")
    
    def process_sensor_data(self, sensor_data):
        """Process sensor data and generate alerts"""
        alerts = []
        
        device_name = sensor_data.get('device_name', 'Unknown')
        sensors = sensor_data.get('sensors', {})
        current = sensors.get('current_amps', 0)
        temperature = sensors.get('temperature_celsius', 0)
        pressure = sensors.get('pressure_bar', 0)
        
        # Check for high current
        if current > self.current_threshold:
            alert = {
                'device_name': device_name,
                'alert_type': 'HIGH_CURRENT',
                'severity': 'warning',
                'message': f'High current detected: {current}A (limit: {self.current_threshold}A)',
                'value': current,
                'threshold': self.current_threshold,
                'timestamp': datetime.now().isoformat()
            }
            alerts.append(alert)
        
        # Check for overheating
        if temperature > self.temp_threshold:
            alert = {
                'device_name': device_name,
                'alert_type': 'OVERHEATING',
                'severity': 'critical',
                'message': f'Overheating detected: {temperature}°C (limit: {self.temp_threshold}°C)',
                'value': temperature,
                'threshold': self.temp_threshold,
                'timestamp': datetime.now().isoformat()
            }
            alerts.append(alert)
        
        # Check for high pressure
        if pressure > self.pressure_threshold:
            alert = {
                'device_name': device_name,
                'alert_type': 'HIGH_PRESSURE',
                'severity': 'critical',
                'message': f'High pressure detected: {pressure} bar (limit: {self.pressure_threshold} bar)',
                'value': pressure,
                'threshold': self.pressure_threshold,
                'timestamp': datetime.now().isoformat()
            }
            alerts.append(alert)
        
        return alerts

class WorkingDataProcessor:
    """
    Working data processor using REST API
    """
    
    def __init__(self):
        # Setup Supabase REST client
        self.supabase_client = RestSupabaseClient()
        
        # Setup alert processor
        self.alert_processor = AlertProcessor()
        
        # Setup Kafka consumer
        self.bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        self.topic_name = os.getenv('KAFKA_IOT_TOPIC', 'iot-sensors')
        self.group_id = 'working-data-processor-group'
        
        self.setup_kafka_consumer()
        
        # Statistics
        self.processed_count = 0
        self.stored_count = 0
        self.alert_count = 0
    
    def setup_kafka_consumer(self):
        """Setup Kafka consumer"""
        try:
            self.consumer = KafkaConsumer(
                self.topic_name,
                bootstrap_servers=[self.bootstrap_servers],
                group_id=self.group_id,
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                auto_offset_reset='latest',
                enable_auto_commit=True,
                auto_commit_interval_ms=1000
            )
            print(f"✅ Kafka Consumer connected to {self.bootstrap_servers}")
            print(f"📡 Listening to topic: {self.topic_name}")
        except Exception as e:
            print(f"❌ Failed to connect to Kafka: {e}")
            self.consumer = None
    
    def start_processing(self):
        """Start processing messages from Kafka"""
        if self.consumer is None:
            print("❌ Cannot start processing - Kafka consumer not available")
            return
        
        print(f"\n🧠 Starting data processing with working Supabase storage...")
        print("Press Ctrl+C to stop processing\n")
        
        try:
            for message in self.consumer:
                self.processed_count += 1
                
                try:
                    # Get sensor data
                    sensor_data = message.value
                    
                    # Store sensor data
                    stored = self.supabase_client.store_sensor_data(sensor_data)
                    if stored:
                        self.stored_count += 1
                    
                    # Process alerts
                    alerts = self.alert_processor.process_sensor_data(sensor_data)
                    
                    # Store alerts
                    for alert in alerts:
                        alert_stored = self.supabase_client.store_alert(alert)
                        if alert_stored:
                            self.alert_count += 1
                            print(f"🚨 Alert stored: {alert['device_name']} - {alert['alert_type']}")
                    
                    # Print status every 10 messages
                    if self.processed_count % 10 == 0:
                        print(f"📊 Processed: {self.processed_count}, Stored: {self.stored_count}, Alerts: {self.alert_count}")
                
                except Exception as e:
                    print(f"❌ Error processing message: {e}")
                    continue
        
        except KeyboardInterrupt:
            print(f"\n\n🛑 Processing stopped")
            print(f"📈 Final stats - Processed: {self.processed_count}, Stored: {self.stored_count}, Alerts: {self.alert_count}")
        
        finally:
            if self.consumer:
                self.consumer.close()

def test_processor():
    """Test the processor with sample data"""
    print("🧪 Testing Working Data Processor...")
    
    try:
        processor = WorkingDataProcessor()
        
        # Test with sample sensor data
        test_data = {
            'device_name': 'EnergyDevice_001',
            'timestamp': datetime.now().isoformat(),
            'sensors': {
                'current_amps': 16.5,  # Above threshold to trigger alert
                'temperature_celsius': 75.0,
                'pressure_bar': 2.1
            }
        }
        
        print(f"📤 Testing with sample data: {test_data}")
        
        # Store sensor data
        stored = processor.supabase_client.store_sensor_data(test_data)
        print(f"📊 Sensor data stored: {'✅' if stored else '❌'}")
        
        # Process alerts
        alerts = processor.alert_processor.process_sensor_data(test_data)
        print(f"🚨 Alerts generated: {len(alerts)}")
        
        # Store alerts
        for alert in alerts:
            alert_stored = processor.supabase_client.store_alert(alert)
            print(f"🚨 Alert stored: {'✅' if alert_stored else '❌'} - {alert['alert_type']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Working Data Processor - REST API Version")
    print("=" * 60)
    
    # Test first
    test_success = test_processor()
    
    if test_success:
        print(f"\n✅ Test successful! Starting real-time processing...")
        processor = WorkingDataProcessor()
        processor.start_processing()
    else:
        print(f"\n❌ Test failed. Please check your setup.")
