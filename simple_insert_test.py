"""
Simple insert test to match your exact Supabase schema
"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def simple_insert_test():
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json'
    }
    
    # Based on your screenshot, let's try to match the visible columns
    # I can see: id, device_..., device_name, timestamp, current_amp...
    
    test_data = {
        'device_name': 'EnergyDevice_001',
        'timestamp': datetime.now().isoformat() + 'Z',  # Add Z for UTC
        'current_amps': 12.5,
        'temperature_celsius': 75.0,
        'pressure_bar': 2.1
    }
    
    print("🧪 Testing simple insert...")
    print(f"📋 Data: {test_data}")
    
    try:
        response = requests.post(
            f"{supabase_url}/rest/v1/sensor_readings",
            headers=headers,
            json=test_data
        )
        
        print(f"📡 Status: {response.status_code}")
        print(f"📋 Response: {response.text}")
        
        if response.status_code == 201:
            print("✅ SUCCESS! Data inserted")
            return True
        else:
            print("❌ Failed to insert")
            
            # Try with different timestamp format
            print("\n🔄 Trying with different timestamp format...")
            test_data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            response2 = requests.post(
                f"{supabase_url}/rest/v1/sensor_readings",
                headers=headers,
                json=test_data
            )
            
            print(f"📡 Status: {response2.status_code}")
            print(f"📋 Response: {response2.text}")
            
            if response2.status_code == 201:
                print("✅ SUCCESS with different timestamp format!")
                return True
            
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_alerts_table():
    """Test the alerts table which seemed to work before"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json'
    }
    
    test_alert = {
        'device_name': 'EnergyDevice_001',
        'alert_type': 'HIGH_CURRENT',
        'severity': 'warning',
        'message': 'Test alert',
        'sensor_value': 16.5,
        'unit': 'A',
        'timestamp': datetime.now().isoformat() + 'Z'
    }
    
    print("\n🚨 Testing alerts table...")
    print(f"📋 Data: {test_alert}")
    
    try:
        response = requests.post(
            f"{supabase_url}/rest/v1/alerts",
            headers=headers,
            json=test_alert
        )
        
        print(f"📡 Status: {response.status_code}")
        print(f"📋 Response: {response.text}")
        
        if response.status_code == 201:
            print("✅ SUCCESS! Alert inserted")
            return True
        else:
            print("❌ Failed to insert alert")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Simple Insert Test")
    print("=" * 40)
    
    sensor_success = simple_insert_test()
    alert_success = test_alerts_table()
    
    print(f"\n📊 Results:")
    print(f"Sensor readings: {'✅' if sensor_success else '❌'}")
    print(f"Alerts: {'✅' if alert_success else '❌'}")
    
    if sensor_success and alert_success:
        print("\n🎉 Both tables are working! Check your Supabase dashboard.")
    elif alert_success:
        print("\n⚠️ Alerts working, but sensor_readings has issues.")
        print("💡 Check if sensor_readings table has additional required fields.")
    else:
        print("\n❌ Both tables have issues. Check your table permissions and schema.")
