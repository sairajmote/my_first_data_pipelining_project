"""
Simple Supabase Connection Test
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_supabase_rest():
    """Test Supabase connection using REST API directly"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    print("🔍 Testing Supabase REST API connection...")
    print(f"URL: {supabase_url[:30]}..." if supabase_url else "❌ Missing SUPABASE_URL")
    print(f"Key: {supabase_key[:30]}..." if supabase_key else "❌ Missing SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials in .env file")
        return False
    
    try:
        # Test sensor_readings table
        headers = {
            'apikey': supabase_key,
            'Authorization': f'Bearer {supabase_key}',
            'Content-Type': 'application/json'
        }
        
        # Test if sensor_readings table exists
        response = requests.get(
            f"{supabase_url}/rest/v1/sensor_readings?select=count",
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ sensor_readings table exists and is accessible")
            data = response.json()
            print(f"📊 Found {len(data)} records in sensor_readings")
        else:
            print(f"❌ sensor_readings table error: {response.status_code} - {response.text}")
        
        # Test alerts table
        response2 = requests.get(
            f"{supabase_url}/rest/v1/alerts?select=count",
            headers=headers
        )
        
        if response2.status_code == 200:
            print("✅ alerts table exists and is accessible")
            data2 = response2.json()
            print(f"📊 Found {len(data2)} records in alerts")
        else:
            print(f"❌ alerts table error: {response2.status_code} - {response2.text}")
            
        return True
        
    except Exception as e:
        print(f"❌ Failed to test Supabase REST API: {e}")
        return False

def test_supabase_python():
    """Test using Python client"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    print("\n🔍 Testing Supabase Python client...")
    
    try:
        from supabase import create_client
        supabase = create_client(supabase_url, supabase_key)
        
        # Simple test query
        result = supabase.table('sensor_readings').select("*").limit(1).execute()
        print(f"✅ Python client connected successfully!")
        print(f"📊 sensor_readings query successful")
        
        # Test alerts table
        result2 = supabase.table('alerts').select("*").limit(1).execute()
        print(f"📊 alerts query successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Python client failed: {e}")
        return False

if __name__ == "__main__":
    # Test both methods
    rest_success = test_supabase_rest()
    python_success = test_supabase_python()
    
    if rest_success:
        print("\n✅ Supabase is accessible via REST API")
    if python_success:
        print("✅ Supabase Python client is working")
    
    if not rest_success and not python_success:
        print("\n❌ Both connection methods failed. Check your Supabase setup.")
