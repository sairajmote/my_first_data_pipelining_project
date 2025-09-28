"""
Check Supabase Database Tables and Data
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

def check_database():
    # Get Supabase credentials
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials in .env file")
        return
    
    try:
        # Create Supabase client (handle version compatibility)
        try:
            supabase: Client = create_client(supabase_url, supabase_key)
        except TypeError as e:
            if "proxy" in str(e):
                # Try older version syntax
                from supabase.client import Client as SupabaseClient
                supabase = SupabaseClient(supabase_url, supabase_key)
            else:
                raise e
        print(f"✅ Connected to Supabase")
        
        # Check sensor_readings table
        print("\n📊 Checking sensor_readings table...")
        try:
            result = supabase.table('sensor_readings').select("count", count="exact").execute()
            print(f"✅ sensor_readings table exists with {result.count} records")
            
            # Get latest 5 records
            latest = supabase.table('sensor_readings').select('*').order('timestamp', desc=True).limit(5).execute()
            if latest.data:
                print("📋 Latest 5 records:")
                for record in latest.data:
                    print(f"   {record['device_name']}: {record['current_amps']}A, {record['temperature_celsius']}°C, {record['pressure_bar']} bar")
            else:
                print("⚠️ No data in sensor_readings table")
                
        except Exception as e:
            print(f"❌ sensor_readings table error: {e}")
            print("💡 Table might not exist - need to create it")
        
        # Check alerts table
        print("\n🚨 Checking alerts table...")
        try:
            result = supabase.table('alerts').select("count", count="exact").execute()
            print(f"✅ alerts table exists with {result.count} records")
            
            # Get latest 3 alerts
            latest = supabase.table('alerts').select('*').order('timestamp', desc=True).limit(3).execute()
            if latest.data:
                print("📋 Latest 3 alerts:")
                for alert in latest.data:
                    print(f"   {alert['device_name']}: {alert['alert_type']} - {alert['message']}")
            else:
                print("⚠️ No alerts in alerts table")
                
        except Exception as e:
            print(f"❌ alerts table error: {e}")
            print("💡 Table might not exist - need to create it")
            
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")

if __name__ == "__main__":
    check_database()
