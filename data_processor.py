"""
Enhanced Data Processing System - Step 3
Advanced core processing with intelligent alert engine
Features: Schema validation, error handling, alert deduplication, multi-level alerts
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
# Removed problematic supabase import - using REST API only

# Load environment variables from .env file
load_dotenv()

class MessageValidator:
    """
    Core Processing: Schema validation and data quality checks
    Ensures incoming messages are valid before processing
    """
    
    def __init__(self):
        # Define expected message schema
        self.required_fields = ['device_id', 'device_name', 'timestamp', 'sensors']
        self.required_sensors = ['current_amps', 'temperature_celsius', 'pressure_bar']
        
        # Data quality thresholds
        self.sensor_ranges = {
            'current_amps': (0, 50),      # 0-50 Amps reasonable range
            'temperature_celsius': (-20, 150),  # -20 to 150°C reasonable range  
            'pressure_bar': (0, 10)       # 0-10 bar reasonable range
        }
        
        self.validation_stats = {
            'total_messages': 0,
            'valid_messages': 0,
            'invalid_messages': 0,
            'validation_errors': defaultdict(int)
        }
    
    def validate_message(self, message_data):
        """
        Validate message structure and data quality
        Returns (is_valid, error_list)
        """
        self.validation_stats['total_messages'] += 1
        errors = []
        
        try:
            # Check required top-level fields
            for field in self.required_fields:
                if field not in message_data:
                    errors.append(f"Missing required field: {field}")
                    self.validation_stats['validation_errors'][f'missing_{field}'] += 1
            
            # Check sensors object
            if 'sensors' in message_data:
                sensors = message_data['sensors']
                
                # Check required sensor fields
                for sensor in self.required_sensors:
                    if sensor not in sensors:
                        errors.append(f"Missing sensor: {sensor}")
                        self.validation_stats['validation_errors'][f'missing_sensor_{sensor}'] += 1
                    else:
                        # Validate sensor value ranges
                        value = sensors[sensor]
                        if not isinstance(value, (int, float)):
                            errors.append(f"Invalid {sensor} type: {type(value)}")
                            self.validation_stats['validation_errors'][f'invalid_type_{sensor}'] += 1
                        else:
                            min_val, max_val = self.sensor_ranges[sensor]
                            if not (min_val <= value <= max_val):
                                errors.append(f"Out of range {sensor}: {value} (valid: {min_val}-{max_val})")
                                self.validation_stats['validation_errors'][f'out_of_range_{sensor}'] += 1
            
            # Validate timestamp format
            if 'timestamp' in message_data:
                try:
                    datetime.fromisoformat(message_data['timestamp'].replace('Z', '+00:00'))
                except ValueError:
                    errors.append("Invalid timestamp format")
                    self.validation_stats['validation_errors']['invalid_timestamp'] += 1
            
            # Update stats
            if errors:
                self.validation_stats['invalid_messages'] += 1
                return False, errors
            else:
                self.validation_stats['valid_messages'] += 1
                return True, []
                
        except Exception as e:
            errors.append(f"Validation exception: {str(e)}")
            self.validation_stats['invalid_messages'] += 1
            self.validation_stats['validation_errors']['validation_exception'] += 1
            return False, errors

class AlertEngine:
    """
    Advanced Alert Engine with deduplication, rate limiting, and multi-level alerts
    """
    
    def __init__(self):
        # Alert configuration
        self.alert_levels = {
            'INFO': {'priority': 1, 'cooldown': 300},      # 5 minutes
            'WARNING': {'priority': 2, 'cooldown': 180},   # 3 minutes  
            'CRITICAL': {'priority': 3, 'cooldown': 60},   # 1 minute
            'EMERGENCY': {'priority': 4, 'cooldown': 30}   # 30 seconds
        }
        
        # Alert deduplication - track recent alerts per device
        self.recent_alerts = defaultdict(lambda: defaultdict(deque))
        
        # Alert statistics
        self.alert_stats = {
            'total_alerts': 0,
            'deduplicated_alerts': 0,
            'alerts_by_level': defaultdict(int),
            'alerts_by_device': defaultdict(int),
            'alerts_by_type': defaultdict(int)
        }
        
        print(f"🎯 Advanced Alert Engine initialized")
        print(f"   📊 Alert levels: {list(self.alert_levels.keys())}")
        print(f"   🔄 Deduplication enabled")
    
    def should_send_alert(self, device_name, alert_type, alert_level):
        """
        Check if alert should be sent based on deduplication rules
        """
        now = datetime.now()
        cooldown_seconds = self.alert_levels[alert_level]['cooldown']
        
        # Get recent alerts for this device and type
        recent = self.recent_alerts[device_name][alert_type]
        
        # Remove old alerts outside cooldown period
        cutoff_time = now - timedelta(seconds=cooldown_seconds)
        while recent and recent[0] < cutoff_time:
            recent.popleft()
        
        # If no recent alerts, allow this one
        if not recent:
            recent.append(now)
            return True
        
        # Alert is within cooldown period - deduplicate
        self.alert_stats['deduplicated_alerts'] += 1
        return False
    
    def create_alert(self, alert_type, device_name, message, value, threshold, severity='WARNING'):
        """
        Create a structured alert with metadata
        """
        alert = {
            'id': f"{device_name}_{alert_type}_{int(time.time())}",
            'timestamp': datetime.now().isoformat(),
            'device_name': device_name,
            'alert_type': alert_type,
            'severity': severity,
            'message': message,
            'value': value,
            'threshold': threshold,
            'priority': self.alert_levels[severity]['priority']
        }
        
        # Update statistics
        self.alert_stats['total_alerts'] += 1
        self.alert_stats['alerts_by_level'][severity] += 1
        self.alert_stats['alerts_by_device'][device_name] += 1
        self.alert_stats['alerts_by_type'][alert_type] += 1
        
        return alert
    
    def get_alert_summary(self):
        """
        Get summary of alert statistics
        """
        return {
            'total_alerts': self.alert_stats['total_alerts'],
            'deduplicated_count': self.alert_stats['deduplicated_alerts'],
            'by_level': dict(self.alert_stats['alerts_by_level']),
            'top_devices': dict(sorted(self.alert_stats['alerts_by_device'].items(), 
                                     key=lambda x: x[1], reverse=True)[:5]),
            'by_type': dict(self.alert_stats['alerts_by_type'])
        }

class AlertProcessor:
    """
    This class handles processing alerts from sensor data
    Applies business rules to determine when readings are dangerous
    """
    
    def __init__(self):
        # Get alert thresholds from environment variables (no hardcoding!)
        self.current_threshold = float(os.getenv('CURRENT_ALERT_THRESHOLD', 15.0))
        self.temp_threshold = float(os.getenv('TEMPERATURE_ALERT_THRESHOLD', 80.0))
        self.pressure_threshold = float(os.getenv('PRESSURE_ALERT_THRESHOLD', 2.5))
        
        # Initialize core processing components
        self.validator = MessageValidator()
        self.alert_engine = AlertEngine()
        
        # Keep track of statistics
        self.total_messages = 0
        self.processed_messages = 0
        self.failed_messages = 0
        self.alert_count = 0  # Track total alerts generated
        self.device_stats = {}  # Track stats per device
        
        print(f"🎯 Enhanced Alert Processor initialized with thresholds:")
        print(f"   Current: > {self.current_threshold}A")
        print(f"   Temperature: > {self.temp_threshold}°C")
        print(f"   Pressure: > {self.pressure_threshold} bar")
    
    def process_sensor_data(self, sensor_data):
        """
        Enhanced processing with validation, error handling, and smart alerting
        """
        
        self.total_messages += 1
        
        # Step 1: Core Processing - Validate incoming message
        is_valid, validation_errors = self.validator.validate_message(sensor_data)
        
        if not is_valid:
            self.failed_messages += 1
            print(f"❌ Invalid message: {validation_errors}")
            return []
        
        self.processed_messages += 1
        device_name = sensor_data.get('device_name', 'Unknown')
        
        # Initialize device stats if first time seeing this device
        if device_name not in self.device_stats:
            self.device_stats[device_name] = {
                'messages': 0,
                'alerts': 0,
                'last_seen': None,
                'validation_failures': 0
            }
        
        # Update device stats
        self.device_stats[device_name]['messages'] += 1
        self.device_stats[device_name]['last_seen'] = sensor_data.get('timestamp')
        
        # Extract sensor readings from the validated message
        sensors = sensor_data.get('sensors', {})
        current = sensors.get('current_amps', 0)
        temperature = sensors.get('temperature_celsius', 0)
        pressure = sensors.get('pressure_bar', 0)
        
        # Step 2: Apply business rules with enhanced alert engine
        alerts_to_send = []
        
        # Rule 1: High Current Check
        if current > self.current_threshold:
            severity = 'CRITICAL' if current > self.current_threshold * 1.2 else 'WARNING'
            
            if self.alert_engine.should_send_alert(device_name, 'HIGH_CURRENT', severity):
                alert = self.alert_engine.create_alert(
                    alert_type='HIGH_CURRENT',
                    device_name=device_name,
                    message=f'High current detected: {current}A (limit: {self.current_threshold}A)',
                    value=current,
                    threshold=self.current_threshold,
                    severity=severity
                )
                alerts_to_send.append(alert)
        
        # Rule 2: Overheating Check  
        if temperature > self.temp_threshold:
            severity = 'EMERGENCY' if temperature > self.temp_threshold * 1.1 else 'CRITICAL'
            
            if self.alert_engine.should_send_alert(device_name, 'OVERHEATING', severity):
                alert = self.alert_engine.create_alert(
                    alert_type='OVERHEATING',
                    device_name=device_name,
                    message=f'Overheating detected: {temperature}°C (limit: {self.temp_threshold}°C)',
                    value=temperature,
                    threshold=self.temp_threshold,
                    severity=severity
                )
                alerts_to_send.append(alert)
        
        # Rule 3: High Pressure Check
        if pressure > self.pressure_threshold:
            severity = 'EMERGENCY' if pressure > self.pressure_threshold * 1.1 else 'CRITICAL'
            
            if self.alert_engine.should_send_alert(device_name, 'HIGH_PRESSURE', severity):
                alert = self.alert_engine.create_alert(
                    alert_type='HIGH_PRESSURE',
                    device_name=device_name,
                    message=f'High pressure detected: {pressure} bar (limit: {self.pressure_threshold} bar)',
                    value=pressure,
                    threshold=self.pressure_threshold,
                    severity=severity
                )
                alerts_to_send.append(alert)
        
        # Step 3: Handle alerts that passed deduplication
        if alerts_to_send:
            self.device_stats[device_name]['alerts'] += len(alerts_to_send)
            self.alert_count += len(alerts_to_send)  # Update total alert count
            self.handle_alerts(device_name, alerts_to_send, sensor_data)
        
        return alerts_to_send
    
    def handle_alerts(self, device_name, alerts, sensor_data):
        """
        Handle alerts - display them with context
        In a real system, this would send emails, SMS, or trigger automatic shutdowns
        """
        
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        print(f"\n🚨 ALERT DETECTED at {timestamp}")
        print("=" * 60)
        print(f"📍 Device: {device_name}")
        
        for alert in alerts:
            # Choose emoji and color based on severity
            if alert['severity'] == 'WARNING':
                emoji = "⚠️ "
                severity_text = "WARNING"
            else:
                emoji = "🔥"
                severity_text = "CRITICAL"
            
            print(f"{emoji} {severity_text}: {alert.get('alert_type', 'Unknown')}")
            print(f"   📊 {alert['message']}")
            print(f"   ⚡ Value: {alert.get('value', 'N/A')} (Threshold: {alert.get('threshold', 'N/A')})")
        
        # Show current readings for context
        sensors = sensor_data.get('sensors', {})
        print(f"\n📋 Current Device Readings:")
        print(f"   🔌 Current: {sensors.get('current_amps', 0)}A")
        print(f"   🌡️  Temperature: {sensors.get('temperature_celsius', 0)}°C")
        print(f"   💨 Pressure: {sensors.get('pressure_bar', 0)} bar")
        print(f"   🕐 Timestamp: {sensor_data.get('timestamp', 'Unknown')}")
        print("=" * 60)
    
    def print_statistics(self):
        """
        Enhanced statistics with validation and alert engine metrics
        """
        print(f"\n📈 ENHANCED PROCESSING STATISTICS:")
        print("=" * 50)
        
        # Core processing stats
        print(f"📨 Message Processing:")
        print(f"   Total received: {self.total_messages}")
        print(f"   Successfully processed: {self.processed_messages}")
        print(f"   Failed validation: {self.failed_messages}")
        
        if self.total_messages > 0:
            success_rate = (self.processed_messages / self.total_messages * 100)
            print(f"   Success rate: {success_rate:.1f}%")
        
        # Validation statistics
        val_stats = self.validator.validation_stats
        print(f"\n🔍 Validation Details:")
        print(f"   Valid messages: {val_stats['valid_messages']}")
        print(f"   Invalid messages: {val_stats['invalid_messages']}")
        
        if val_stats['validation_errors']:
            print(f"   Top validation errors:")
            sorted_errors = sorted(val_stats['validation_errors'].items(), 
                                 key=lambda x: x[1], reverse=True)
            for error, count in sorted_errors[:3]:
                print(f"     - {error}: {count}")
        
        # Alert engine statistics
        alert_summary = self.alert_engine.get_alert_summary()
        print(f"\n🚨 Alert Engine Stats:")
        print(f"   Total alerts: {alert_summary['total_alerts']}")
        print(f"   Deduplicated: {alert_summary['deduplicated_count']}")
        
        if alert_summary['by_level']:
            print(f"   By severity:")
            for level, count in alert_summary['by_level'].items():
                print(f"     - {level}: {count}")
        
        if alert_summary['top_devices']:
            print(f"   Top alerting devices:")
            for device, count in list(alert_summary['top_devices'].items())[:3]:
                print(f"     - {device}: {count} alerts")
        
        print(f"\n📱 Active devices: {len(self.device_stats)}")
        print("=" * 50)

class DataProcessor:
    """
    Main Data Processing System
    Combines Kafka consumer with alert processing
    """
    
    def __init__(self):
        # Get Kafka settings from environment variables
        self.bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        self.topic_name = os.getenv('KAFKA_IOT_TOPIC', 'iot-sensors')
        self.group_id = 'data-processor-group'
        
        # Create alert processor
        self.alert_processor = AlertProcessor()
        
        # Setup Supabase connection
        self.setup_supabase()
        
        # Setup Kafka consumer
        self.setup_kafka_consumer()
    
    def setup_supabase(self):
        """Setup Supabase database connection"""
        try:
            # Get Supabase credentials from environment variables
            self.supabase_url = os.getenv('SUPABASE_URL')
            self.supabase_key = os.getenv('SUPABASE_KEY')
            
            if not self.supabase_url or not self.supabase_key:
                print("❌ Missing Supabase credentials in .env file")
                self.supabase = None
                return
            
            # Create Supabase client with error handling
            try:
                self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
                print(f"✅ Connected to Supabase database")
                
                # Test connection with a simple query
                result = self.supabase.table('sensor_readings').select("*").limit(1).execute()
                print(f"📊 Database ready - sensor_readings table accessible")
                
                # Test alerts table
                result2 = self.supabase.table('alerts').select("*").limit(1).execute()
                print(f"📊 Database ready - alerts table accessible")
                
            except Exception as client_error:
                print(f"❌ Supabase client initialization failed: {client_error}")
                print("🔄 Falling back to REST API mode...")
                self.supabase = None
                # Set up REST API fallback
                self.setup_rest_fallback()
            
        except Exception as e:
            print(f"❌ Failed to setup Supabase: {e}")
            self.supabase = None
            self.setup_rest_fallback()
    
    def setup_rest_fallback(self):
        """Setup REST API fallback for Supabase operations"""
        self.rest_headers = {
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}',
            'Content-Type': 'application/json'
        }
        print("📡 REST API fallback configured")
    
    def store_sensor_data(self, sensor_data):
        """Store sensor data in Supabase database"""
        try:
            # Prepare data for database
            db_record = {
                'device_id': sensor_data['device_id'],
                'device_name': sensor_data['device_name'],
                'timestamp': sensor_data['timestamp'],
                'current_amps': sensor_data['sensors']['current_amps'],
                'temperature_celsius': sensor_data['sensors']['temperature_celsius'],
                'pressure_bar': sensor_data['sensors']['pressure_bar']
            }
            
            # Try Python client first
            if self.supabase:
                try:
                    result = self.supabase.table('sensor_readings').insert(db_record).execute()
                    return True
                except Exception as e:
                    print(f"⚠️ Python client failed, trying REST API: {e}")
            
            # Fallback to REST API
            if hasattr(self, 'rest_headers'):
                # Fix timestamp format
                if 'timestamp' in db_record and not db_record['timestamp'].endswith('Z'):
                    db_record['timestamp'] += 'Z'
                    
                response = requests.post(
                    f"{self.supabase_url}/rest/v1/sensor_readings",
                    headers=self.rest_headers,
                    json=db_record
                )
                if response.status_code in [200, 201]:
                    return True
                else:
                    print(f"⚠️ Sensor storage failed, storing as alert instead")
                    # Store as informational alert if sensor_readings fails
                    fallback_alert = {
                        'device_name': db_record.get('device_name'),
                        'alert_type': 'SENSOR_DATA',
                        'severity': 'info',
                        'message': f"Sensor: {db_record.get('current_amps')}A, {db_record.get('temperature_celsius')}°C",
                        'sensor_value': db_record.get('current_amps', 0),
                        'unit': 'A',
                        'timestamp': db_record.get('timestamp')
                    }
                    alert_response = requests.post(
                        f"{self.supabase_url}/rest/v1/alerts",
                        headers=self.rest_headers,
                        json=fallback_alert
                    )
                    return alert_response.status_code in [200, 201]
            
            return False
            
        except Exception as e:
            print(f"❌ Failed to store sensor data: {e}")
            return False
    
    def store_alerts(self, alerts):
        """Store alerts in Supabase database"""
        if not alerts:
            return
        
        try:
            for alert in alerts:
                # Prepare alert data for database
                db_alert = {
                    'device_name': alert.get('device_name', ''),
                    'alert_type': alert.get('alert_type', ''),
                    'message': alert.get('message', ''),
                    'severity': alert.get('severity', 'warning'),
                    'sensor_value': alert.get('value', 0),
                    'unit': '',
                    'timestamp': alert.get('timestamp', datetime.now().isoformat())
                }
                
                # Try Python client first
                if self.supabase:
                    try:
                        self.supabase.table('alerts').insert(db_alert).execute()
                        continue
                    except Exception as e:
                        print(f"⚠️ Python client failed for alert, trying REST API: {e}")
                
                # Fallback to REST API (use existing alerts table)
                if hasattr(self, 'rest_headers'):
                    response = requests.post(
                        f"{self.supabase_url}/rest/v1/alerts",
                        headers=self.rest_headers,
                        json=db_alert
                    )
                    if response.status_code not in [200, 201]:
                        print(f"❌ REST API failed for alert: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Failed to store alerts: {e}")
    
    def setup_kafka_consumer(self):
        """Setup Kafka consumer"""
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
            print(f"✅ Data Processor connected to Kafka at {self.bootstrap_servers}")
            print(f"📡 Processing messages from topic: {self.topic_name}")
            print(f"👥 Consumer group: {self.group_id}")
        except Exception as e:
            print(f"❌ Failed to connect to Kafka: {e}")
            print(f"💡 Make sure Kafka is running on {self.bootstrap_servers}")
            self.consumer = None
    
    def start_processing(self):
        """
        Start processing messages from Kafka with alert rules
        This is the main processing loop
        """
        
        if self.consumer is None:
            print("❌ Cannot start processing - Kafka consumer not available")
            return
        
        print(f"\n🧠 Starting intelligent data processing...")
        print("Press Ctrl+C to stop processing\n")
        
        try:
            message_count = 0
            
            # Keep reading and processing messages forever
            for message in self.consumer:
                message_count += 1
                
                try:
                    # Get the sensor data from the message
                    sensor_data = message.value
                    
                    # Store sensor data in Supabase database
                    stored = self.store_sensor_data(sensor_data)
                    
                    # Process the data and check for alerts (this is the key part!)
                    alerts = self.alert_processor.process_sensor_data(sensor_data)
                    
                    # Store alerts in database if any were generated
                    if alerts:
                        self.store_alerts(alerts)
                    
                    # Print a simple status every 50 messages (to avoid spam)
                    if message_count % 50 == 0:
                        print(f"📊 Processed {message_count} messages... "
                              f"(Alerts: {self.alert_processor.alert_count}) "
                              f"{'✅ DB' if stored else '❌ DB'}")
                    
                    # Print detailed statistics every 200 messages
                    if message_count % 200 == 0:
                        self.alert_processor.print_statistics()
                
                except Exception as e:
                    print(f"❌ Error processing message: {e}")
                    continue
        
        except KeyboardInterrupt:
            print("\n\n🛑 Data processing stopped by user")
            self.alert_processor.print_statistics()
            print("👋 Goodbye!")
        
        finally:
            if self.consumer:
                self.consumer.close()
                print("📪 Kafka consumer connection closed")

def main():
    """
    Main function - starts the data processing system with alert rules
    """
    
    print("🧠 Starting IoT Data Processing System with Alert Rules...")
    print("=" * 60)
    
    # Create and start the data processor
    processor = DataProcessor()
    processor.start_processing()

# This runs when the script is executed
if __name__ == "__main__":
    main()
