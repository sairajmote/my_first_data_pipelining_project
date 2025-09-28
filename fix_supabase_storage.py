"""
Fix Supabase Storage - Direct REST API approach
This bypasses the problematic Python client and uses direct REST API calls
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def test_table_structure():
    """Test what tables exist and their structure"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json'
    }
    
    print("🔍 Testing table structure...")
    
    # Test sensor_readings table
    try:
        response = requests.get(
            f"{supabase_url}/rest/v1/sensor_readings?limit=1",
            headers=headers
        )
        print(f"📊 sensor_readings status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data:
                print(f"📋 sensor_readings structure: {list(data[0].keys())}")
            else:
                print("📋 sensor_readings table exists but is empty")
        else:
            print(f"❌ sensor_readings error: {response.text}")
    except Exception as e:
        print(f"❌ sensor_readings test failed: {e}")
    
    # Test alerts table
    try:
        response = requests.get(
            f"{supabase_url}/rest/v1/alerts?limit=1",
            headers=headers
        )
        print(f"🚨 alerts status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data:
                print(f"📋 alerts structure: {list(data[0].keys())}")
            else:
                print("📋 alerts table exists but is empty")
        else:
            print(f"❌ alerts error: {response.text}")
    except Exception as e:
        print(f"❌ alerts test failed: {e}")

def store_test_sensor_data():
    """Store test sensor data matching dashboard expectations"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json'
    }
    
    # Test data matching dashboard structure
    test_data = {
        'device_name': 'EnergyDevice_001',
        'timestamp': datetime.now().isoformat(),
        'current_amps': 12.5,
        'temperature_celsius': 75.0,
        'pressure_bar': 2.1
    }
    
    print(f"\n📤 Storing test sensor data: {test_data}")
    
    try:
        response = requests.post(
            f"{supabase_url}/rest/v1/sensor_readings",
            headers=headers,
            json=test_data
        )
        
        print(f"📡 Response status: {response.status_code}")
        print(f"📋 Response: {response.text}")
        
        if response.status_code in [200, 201]:
            print("✅ Sensor data stored successfully!")
            return True
        else:
            print(f"❌ Failed to store sensor data")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def store_test_alert():
    """Store test alert data"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json'
    }
    
    # Test alert data
    test_alert = {
        'device_name': 'EnergyDevice_001',
        'alert_type': 'HIGH_CURRENT',
        'message': 'High current detected: 16.5A (limit: 15.0A)',
        'severity': 'warning',
        'sensor_value': 16.5,
        'timestamp': datetime.now().isoformat()
    }
    
    print(f"\n🚨 Storing test alert: {test_alert}")
    
    try:
        response = requests.post(
            f"{supabase_url}/rest/v1/alerts",
            headers=headers,
            json=test_alert
        )
        
        print(f"📡 Response status: {response.status_code}")
        print(f"📋 Response: {response.text}")
        
        if response.status_code in [200, 201]:
            print("✅ Alert stored successfully!")
            return True
        else:
            print(f"❌ Failed to store alert")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def create_rest_data_processor():
    """Create a simple data processor using only REST API"""
    
    class RestSupabaseProcessor:
        def __init__(self):
            self.supabase_url = os.getenv('SUPABASE_URL')
            self.supabase_key = os.getenv('SUPABASE_KEY')
            self.headers = {
                'apikey': self.supabase_key,
                'Authorization': f'Bearer {self.supabase_key}',
                'Content-Type': 'application/json'
            }
            print("✅ REST API processor initialized")
        
        def store_sensor_data(self, sensor_data):
            """Store sensor data via REST API"""
            try:
                # Prepare data matching table structure
                db_record = {
                    'device_name': sensor_data.get('device_name'),
                    'timestamp': sensor_data.get('timestamp'),
                    'current_amps': sensor_data.get('sensors', {}).get('current_amps'),
                    'temperature_celsius': sensor_data.get('sensors', {}).get('temperature_celsius'),
                    'pressure_bar': sensor_data.get('sensors', {}).get('pressure_bar')
                }
                
                response = requests.post(
                    f"{self.supabase_url}/rest/v1/sensor_readings",
                    headers=self.headers,
                    json=db_record
                )
                
                return response.status_code in [200, 201]
                
            except Exception as e:
                print(f"❌ Failed to store sensor data: {e}")
                return False
        
        def store_alert(self, alert_data):
            """Store alert via REST API"""
            try:
                db_record = {
                    'device_name': alert_data.get('device_name'),
                    'alert_type': alert_data.get('alert_type'),
                    'message': alert_data.get('message'),
                    'severity': alert_data.get('severity'),
                    'sensor_value': alert_data.get('value'),
                    'timestamp': alert_data.get('timestamp')
                }
                
                response = requests.post(
                    f"{self.supabase_url}/rest/v1/alerts",
                    headers=self.headers,
                    json=db_record
                )
                
                return response.status_code in [200, 201]
                
            except Exception as e:
                print(f"❌ Failed to store alert: {e}")
                return False
    
    return RestSupabaseProcessor()

if __name__ == "__main__":
    print("🔧 Fixing Supabase Storage Issues...")
    print("=" * 50)
    
    # Test table structure
    test_table_structure()
    
    # Test storing data
    sensor_success = store_test_sensor_data()
    alert_success = store_test_alert()
    
    # Create REST processor
    if sensor_success and alert_success:
        print("\n🎉 REST API storage is working!")
        processor = create_rest_data_processor()
        print("✅ REST API processor created successfully")
        
        # Test the processor
        test_sensor = {
            'device_name': 'EnergyDevice_002',
            'timestamp': datetime.now().isoformat(),
            'sensors': {
                'current_amps': 14.2,
                'temperature_celsius': 68.5,
                'pressure_bar': 1.8
            }
        }
        
        test_alert = {
            'device_name': 'EnergyDevice_002',
            'alert_type': 'HIGH_TEMPERATURE',
            'message': 'Temperature alert test',
            'severity': 'warning',
            'value': 85.0,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"\n🧪 Testing processor with sample data...")
        sensor_result = processor.store_sensor_data(test_sensor)
        alert_result = processor.store_alert(test_alert)
        
        print(f"📊 Sensor storage: {'✅' if sensor_result else '❌'}")
        print(f"🚨 Alert storage: {'✅' if alert_result else '❌'}")
        
    else:
        print("\n❌ REST API storage tests failed")
