"""
Debug the sensor_readings table to see what fields are required
"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def test_minimal_sensor_data():
    """Test with minimal required fields only"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json'
    }
    
    print("🔍 Testing sensor_readings table with different field combinations...")
    
    # Test cases with different field combinations
    test_cases = [
        {
            'name': 'All fields',
            'data': {
                'device_name': 'TestDevice',
                'timestamp': datetime.now().isoformat(),
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
                'timestamp': datetime.now().isoformat(),
                'current_amps': 12.5,
                'temperature_celsius': 75.0,
                'pressure_bar': 2.1
            }
        },
        {
            'name': 'Only required fields',
            'data': {
                'device_name': 'TestDevice',
                'timestamp': datetime.now().isoformat()
            }
        },
        {
            'name': 'With id field',
            'data': {
                'id': 1,
                'device_name': 'TestDevice',
                'timestamp': datetime.now().isoformat(),
                'current_amps': 12.5,
                'temperature_celsius': 75.0,
                'pressure_bar': 2.1
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\n🧪 Test {i+1}: {test_case['name']}")
        print(f"📋 Data: {test_case['data']}")
        
        try:
            response = requests.post(
                f"{supabase_url}/rest/v1/sensor_readings",
                headers=headers,
                json=test_case['data']
            )
            
            print(f"📡 Status: {response.status_code}")
            if response.status_code == 201:
                print("✅ SUCCESS!")
                result = response.json()
                print(f"📊 Inserted: {result}")
                break  # Stop on first success
            else:
                print(f"❌ Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")

def check_existing_data_structure():
    """Check the structure of existing data"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json'
    }
    
    print("\n📊 Checking existing data structure...")
    
    try:
        response = requests.get(
            f"{supabase_url}/rest/v1/sensor_readings?limit=1",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if data:
                print("✅ Found existing data:")
                print(f"📋 Sample record: {data[0]}")
                print(f"📋 Fields: {list(data[0].keys())}")
            else:
                print("📋 Table exists but is empty")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    print("🔍 Debugging sensor_readings table structure...")
    print("=" * 60)
    
    check_existing_data_structure()
    test_minimal_sensor_data()
