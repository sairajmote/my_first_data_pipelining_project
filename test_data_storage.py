"""
Test Data Storage to Supabase
This script tests storing sensor data and alerts directly via REST API
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def test_store_sensor_data():
    """Test storing sensor data via REST API"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials")
        return False
    
    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json'
    }
    
    # Test sensor data
    test_sensor_data = {
        'device_id': 'TEST_001',
        'device_name': 'TestDevice_001',
        'timestamp': datetime.now().isoformat(),
        'current_amps': 12.5,
        'temperature_celsius': 75.0,
        'pressure_bar': 2.1
    }
    
    try:
        print("🧪 Testing sensor data storage...")
        response = requests.post(
            f"{supabase_url}/rest/v1/sensor_readings",
            headers=headers,
            json=test_sensor_data
        )
        
        print(f"📡 Response status: {response.status_code}")
        print(f"📋 Response text: {response.text[:200]}...")
        
        if response.status_code in [200, 201]:
            print("✅ Sensor data stored successfully!")
            try:
                response_data = response.json()
                print(f"📊 Response data: {response_data}")
            except:
                print("📊 Response received but not JSON")
            return True
        else:
            print(f"❌ Failed to store sensor data: {response.status_code}")
            print(f"📋 Full error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception storing sensor data: {e}")
        return False

def test_store_alert():
    """Test storing alert data via REST API"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json'
    }
    
    # Test alert data
    test_alert_data = {
        'device_name': 'TestDevice_001',
        'alert_type': 'HIGH_CURRENT',
        'message': 'Test alert: High current detected',
        'severity': 'WARNING',
        'sensor_value': 16.5,
        'unit': 'A',
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        print("\n🚨 Testing alert storage...")
        response = requests.post(
            f"{supabase_url}/rest/v1/alerts",
            headers=headers,
            json=test_alert_data
        )
        
        if response.status_code in [200, 201]:
            print("✅ Alert stored successfully!")
            print(f"📊 Response: {response.json()}")
            return True
        else:
            print(f"❌ Failed to store alert: {response.status_code}")
            print(f"📋 Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception storing alert: {e}")
        return False

def test_read_data():
    """Test reading data from Supabase"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        print("\n📖 Testing data reading...")
        
        # Read recent sensor data
        response = requests.get(
            f"{supabase_url}/rest/v1/sensor_readings?order=timestamp.desc&limit=5",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {len(data)} recent sensor readings")
            for reading in data[:2]:  # Show first 2
                print(f"   📊 {reading.get('device_name', 'Unknown')} - {reading.get('current_amps', 0)}A")
        
        # Read recent alerts
        response2 = requests.get(
            f"{supabase_url}/rest/v1/alerts?order=timestamp.desc&limit=5",
            headers=headers
        )
        
        if response2.status_code == 200:
            alerts = response2.json()
            print(f"✅ Found {len(alerts)} recent alerts")
            for alert in alerts[:2]:  # Show first 2
                print(f"   🚨 {alert.get('device_name', 'Unknown')} - {alert.get('alert_type', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Exception reading data: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Supabase Data Storage...")
    print("=" * 50)
    
    # Run tests
    sensor_success = test_store_sensor_data()
    alert_success = test_store_alert()
    read_success = test_read_data()
    
    print("\n📋 Test Results:")
    print(f"   Sensor Storage: {'✅' if sensor_success else '❌'}")
    print(f"   Alert Storage: {'✅' if alert_success else '❌'}")
    print(f"   Data Reading: {'✅' if read_success else '❌'}")
    
    if sensor_success and alert_success and read_success:
        print("\n🎉 All tests passed! Supabase storage is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check your Supabase setup.")
