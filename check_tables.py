"""
Check what tables actually exist in Supabase
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def check_all_tables():
    """Check all available tables"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json'
    }
    
    # List of possible table names to check
    table_names = [
        'sensor_readings',
        'alerts', 
        'alert_history',
        'devices',
        'sensor_data'
    ]
    
    print("🔍 Checking which tables exist in Supabase...")
    print("=" * 50)
    
    existing_tables = []
    
    for table_name in table_names:
        try:
            response = requests.get(
                f"{supabase_url}/rest/v1/{table_name}?limit=1",
                headers=headers
            )
            
            if response.status_code == 200:
                print(f"✅ {table_name}: EXISTS")
                existing_tables.append(table_name)
                
                # Get sample data to see structure
                data = response.json()
                if data:
                    print(f"   📋 Sample fields: {list(data[0].keys())}")
                else:
                    print(f"   📋 Table is empty")
                    
            elif response.status_code == 404:
                print(f"❌ {table_name}: NOT FOUND")
            else:
                print(f"⚠️  {table_name}: ERROR {response.status_code}")
                
        except Exception as e:
            print(f"❌ {table_name}: EXCEPTION - {e}")
    
    print("\n📊 Summary:")
    print(f"Found {len(existing_tables)} tables: {existing_tables}")
    
    return existing_tables

def create_missing_tables():
    """Create missing tables if needed"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    print("\n🔧 Note: Tables need to be created in Supabase SQL Editor")
    print("Copy and run this SQL in your Supabase dashboard:")
    print("=" * 50)
    
    sql_script = """
-- Create sensor_readings table if it doesn't exist
CREATE TABLE IF NOT EXISTS sensor_readings (
    id BIGSERIAL PRIMARY KEY,
    device_name VARCHAR(50) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    current_amps DECIMAL(5,2),
    temperature_celsius DECIMAL(5,2),
    pressure_bar DECIMAL(5,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create alert_history table if it doesn't exist
CREATE TABLE IF NOT EXISTS alert_history (
    id BIGSERIAL PRIMARY KEY,
    device_name VARCHAR(50) NOT NULL,
    alert_type VARCHAR(20) NOT NULL,
    severity VARCHAR(10) NOT NULL,
    message TEXT,
    sensor_value DECIMAL(8,2),
    threshold_value DECIMAL(8,2),
    timestamp TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_sensor_readings_device_time 
    ON sensor_readings(device_name, timestamp);

CREATE INDEX IF NOT EXISTS idx_alert_history_device_time 
    ON alert_history(device_name, timestamp);

-- Enable Row Level Security (RLS) if needed
ALTER TABLE sensor_readings ENABLE ROW LEVEL SECURITY;
ALTER TABLE alert_history ENABLE ROW LEVEL SECURITY;

-- Create policies to allow all operations (adjust as needed for production)
CREATE POLICY "Allow all operations on sensor_readings" ON sensor_readings
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all operations on alert_history" ON alert_history
    FOR ALL USING (true) WITH CHECK (true);
"""
    
    print(sql_script)
    print("=" * 50)

if __name__ == "__main__":
    existing_tables = check_all_tables()
    
    if 'sensor_readings' not in existing_tables or 'alert_history' not in existing_tables:
        create_missing_tables()
    else:
        print("\n✅ All required tables exist!")
