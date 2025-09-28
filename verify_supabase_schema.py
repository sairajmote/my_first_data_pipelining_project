"""
Verify Supabase Schema and Insert Test Data
"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def check_table_schema():
    """Check the exact schema of both tables"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json'
    }
    
    print("🔍 Checking table schemas...")
    
    # Check sensor_readings table structure
    print("\n📊 Testing sensor_readings table:")
    test_sensor = {
        'device_name': 'TestDevice_001',
        'timestamp': datetime.now().isoformat(),
        'current_amps': 12.5,
        'temperature_celsius': 75.0,
        'pressure_bar': 2.1
    }
    
    try:
        response = requests.post(
            f"{supabase_url}/rest/v1/sensor_readings",
            headers=headers,
            json=test_sensor
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            print("✅ sensor_readings: Data inserted successfully!")
            result = response.json()
            print(f"📋 Inserted record: {result}")
        else:
            print(f"❌ sensor_readings error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Check alerts table structure
    print("\n🚨 Testing alerts table:")
    test_alert = {
        'device_name': 'TestDevice_001',
        'alert_type': 'HIGH_CURRENT',
        'severity': 'warning',
        'message': 'Test alert message',
        'sensor_value': 16.5,
        'unit': 'A',
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        response = requests.post(
            f"{supabase_url}/rest/v1/alerts",
            headers=headers,
            json=test_alert
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            print("✅ alerts: Data inserted successfully!")
            result = response.json()
            print(f"📋 Inserted record: {result}")
        else:
            print(f"❌ alerts error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

def insert_sample_data():
    """Insert sample data to populate the tables"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json'
    }
    
    print("\n📤 Inserting sample data for testing...")
    
    # Insert multiple sensor readings
    devices = ['EnergyDevice_001', 'EnergyDevice_002', 'EnergyDevice_003']
    
    for i, device in enumerate(devices):
        sensor_data = {
            'device_name': device,
            'timestamp': datetime.now().isoformat(),
            'current_amps': 10.0 + i * 2.5,
            'temperature_celsius': 70.0 + i * 5.0,
            'pressure_bar': 2.0 + i * 0.2
        }
        
        try:
            response = requests.post(
                f"{supabase_url}/rest/v1/sensor_readings",
                headers=headers,
                json=sensor_data
            )
            
            if response.status_code == 201:
                print(f"✅ Inserted sensor data for {device}")
                
                # Create alert if values are high
                if sensor_data['current_amps'] > 12.0:
                    alert_data = {
                        'device_name': device,
                        'alert_type': 'HIGH_CURRENT',
                        'severity': 'warning',
                        'message': f'High current detected: {sensor_data["current_amps"]}A',
                        'sensor_value': sensor_data['current_amps'],
                        'unit': 'A',
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    alert_response = requests.post(
                        f"{supabase_url}/rest/v1/alerts",
                        headers=headers,
                        json=alert_data
                    )
                    
                    if alert_response.status_code == 201:
                        print(f"✅ Inserted alert for {device}")
                    else:
                        print(f"❌ Alert insertion failed: {alert_response.text}")
            else:
                print(f"❌ Sensor data insertion failed: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception for {device}: {e}")

def verify_data():
    """Verify the inserted data"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json'
    }
    
    print("\n📊 Verifying inserted data...")
    
    # Check sensor_readings
    try:
        response = requests.get(
            f"{supabase_url}/rest/v1/sensor_readings?order=timestamp.desc&limit=5",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {len(data)} sensor readings:")
            for reading in data:
                print(f"   📊 {reading.get('device_name')} - {reading.get('current_amps')}A, {reading.get('temperature_celsius')}°C")
        else:
            print(f"❌ Failed to fetch sensor readings: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Check alerts
    try:
        response = requests.get(
            f"{supabase_url}/rest/v1/alerts?order=timestamp.desc&limit=5",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {len(data)} alerts:")
            for alert in data:
                print(f"   🚨 {alert.get('device_name')} - {alert.get('alert_type')} ({alert.get('severity')})")
        else:
            print(f"❌ Failed to fetch alerts: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    print("🔧 Verifying Supabase Schema and Inserting Test Data")
    print("=" * 60)
    
    # Check schema
    check_table_schema()
    
    # Insert sample data
    insert_sample_data()
    
    # Verify data
    verify_data()
    
    print("\n🎉 Schema verification and data insertion complete!")
    print("Now refresh your Supabase dashboard to see the data.")
    print("You can also start the React dashboard to see real data.")
