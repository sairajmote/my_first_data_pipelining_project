"""
Debug Supabase Schema
Find out exactly what the table structure expects
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def debug_sensor_readings_schema():
    """Debug the sensor_readings table schema"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json'
    }
    
    print("🔍 Debugging sensor_readings table...")
    
    # Try different data structures to see what works
    test_cases = [
        {
            'name': 'Basic structure',
            'data': {
                'device_name': 'TestDevice',
                'timestamp': '2025-09-29T01:30:00.000Z',
                'current_amps': 12.5,
                'temperature_celsius': 75.0,
                'pressure_bar': 2.1
            }
        },
        {
            'name': 'With device_id',
            'data': {
                'device_id': 'TEST_001',
                'device_name': 'TestDevice',
                'timestamp': '2025-09-29T01:30:00.000Z',
                'current_amps': 12.5,
                'temperature_celsius': 75.0,
                'pressure_bar': 2.1
            }
        },
        {
            'name': 'Minimal structure',
            'data': {
                'device_name': 'TestDevice',
                'current_amps': 12.5
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🧪 Testing: {test_case['name']}")
        print(f"📋 Data: {test_case['data']}")
        
        try:
            response = requests.post(
                f"{supabase_url}/rest/v1/sensor_readings",
                headers=headers,
                json=test_case['data']
            )
            
            print(f"📡 Status: {response.status_code}")
            if response.status_code != 201:
                print(f"❌ Error: {response.text}")
            else:
                print("✅ Success!")
                break
                
        except Exception as e:
            print(f"❌ Exception: {e}")

def check_existing_data():
    """Check what data already exists in the tables"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json'
    }
    
    print("\n📊 Checking existing data...")
    
    # Check sensor_readings
    try:
        response = requests.get(
            f"{supabase_url}/rest/v1/sensor_readings?limit=3",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 sensor_readings: {len(data)} records found")
            if data:
                print(f"📋 Sample record: {data[0]}")
                print(f"📋 Fields: {list(data[0].keys())}")
        else:
            print(f"❌ sensor_readings error: {response.text}")
    except Exception as e:
        print(f"❌ sensor_readings check failed: {e}")
    
    # Check alerts
    try:
        response = requests.get(
            f"{supabase_url}/rest/v1/alerts?limit=3",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"🚨 alerts: {len(data)} records found")
            if data:
                print(f"📋 Sample alert: {data[0]}")
                print(f"📋 Fields: {list(data[0].keys())}")
        else:
            print(f"❌ alerts error: {response.text}")
    except Exception as e:
        print(f"❌ alerts check failed: {e}")

if __name__ == "__main__":
    print("🔍 Debugging Supabase Schema...")
    print("=" * 50)
    
    check_existing_data()
    debug_sensor_readings_schema()
