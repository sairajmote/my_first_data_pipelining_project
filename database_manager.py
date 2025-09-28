"""
Database Manager - Step 4: Storage Layer
Handles all database operations with Supabase PostgreSQL
Stores sensor readings and alert history for trend analysis
"""

import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from .env file
load_dotenv()

class SupabaseManager:
    """
    Manages all database operations with Supabase PostgreSQL
    Handles sensor data storage and historical queries
    """
    
    def __init__(self):
        # Get Supabase credentials from environment variables (no hardcoding!)
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        
        # Validate credentials
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Missing Supabase credentials in .env file")
        
        # Create Supabase client
        try:
            self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
            print(f"✅ Connected to Supabase database")
            print(f"   🌐 URL: {self.supabase_url}")
            
            # Test connection
            self._test_connection()
            
        except Exception as e:
            print(f"❌ Failed to connect to Supabase: {e}")
            print(f"💡 Check your SUPABASE_URL and SUPABASE_KEY in .env file")
            self.supabase = None
    
    def _test_connection(self):
        """
        Test database connection by checking if tables exist
        """
        try:
            # Try to query sensor_readings table (will fail if table doesn't exist)
            result = self.supabase.table('sensor_readings').select('id').limit(1).execute()
            print(f"   📊 sensor_readings table: ✅ Connected")
            
            # Try to query alert_history table
            result = self.supabase.table('alert_history').select('id').limit(1).execute()
            print(f"   🚨 alert_history table: ✅ Connected")
            
        except Exception as e:
            print(f"   ⚠️  Database tables may not exist yet. Error: {e}")
            print(f"   💡 Run the SQL schema creation script in Supabase SQL Editor")
    
    def save_sensor_reading(self, sensor_data):
        """
        Save sensor reading to database for historical analysis
        """
        if not self.supabase:
            return False
        
        try:
            # Extract data from sensor message
            device_name = sensor_data.get('device_name')
            timestamp = sensor_data.get('timestamp')
            sensors = sensor_data.get('sensors', {})
            
            # Prepare data for database
            db_record = {
                'device_name': device_name,
                'timestamp': timestamp,
                'current_amps': sensors.get('current_amps'),
                'temperature_celsius': sensors.get('temperature_celsius'),
                'pressure_bar': sensors.get('pressure_bar')
            }
            
            # Insert into database
            result = self.supabase.table('sensor_readings').insert(db_record).execute()
            
            # Check if successful
            if result.data:
                return True
            else:
                print(f"❌ Failed to save sensor reading: {result}")
                return False
                
        except Exception as e:
            print(f"❌ Error saving sensor reading: {e}")
            return False
    
    def save_alert(self, alert_data):
        """
        Save alert to database for historical tracking
        """
        if not self.supabase:
            return False
        
        try:
            # Prepare alert data for database
            db_record = {
                'device_name': alert_data.get('device_name'),
                'alert_type': alert_data.get('alert_type'),
                'severity': alert_data.get('severity'),
                'message': alert_data.get('message'),
                'sensor_value': alert_data.get('value'),
                'threshold_value': alert_data.get('threshold'),
                'timestamp': alert_data.get('timestamp')
            }
            
            # Insert into database
            result = self.supabase.table('alert_history').insert(db_record).execute()
            
            # Check if successful
            if result.data:
                return True
            else:
                print(f"❌ Failed to save alert: {result}")
                return False
                
        except Exception as e:
            print(f"❌ Error saving alert: {e}")
            return False
    
    def get_device_history(self, device_name, hours=24):
        """
        Get historical sensor data for a specific device
        Used for trend analysis and dashboards
        """
        if not self.supabase:
            return []
        
        try:
            # Calculate time range
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            # Query database
            result = self.supabase.table('sensor_readings')\
                .select('*')\
                .eq('device_name', device_name)\
                .gte('timestamp', start_time.isoformat())\
                .lte('timestamp', end_time.isoformat())\
                .order('timestamp', desc=False)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            print(f"❌ Error getting device history: {e}")
            return []
    
    def get_alert_history(self, device_name=None, hours=24, severity=None):
        """
        Get alert history with optional filters
        """
        if not self.supabase:
            return []
        
        try:
            # Calculate time range
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            # Build query
            query = self.supabase.table('alert_history').select('*')
            
            # Add filters
            if device_name:
                query = query.eq('device_name', device_name)
            
            if severity:
                query = query.eq('severity', severity)
            
            # Add time range and ordering
            result = query\
                .gte('timestamp', start_time.isoformat())\
                .lte('timestamp', end_time.isoformat())\
                .order('timestamp', desc=True)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            print(f"❌ Error getting alert history: {e}")
            return []
    
    def get_device_statistics(self, hours=24):
        """
        Get statistics for all devices (for dashboard)
        """
        if not self.supabase:
            return {}
        
        try:
            # Calculate time range
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            # Get sensor reading counts per device
            sensor_result = self.supabase.rpc('get_device_sensor_counts', {
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat()
            }).execute()
            
            # Get alert counts per device
            alert_result = self.supabase.rpc('get_device_alert_counts', {
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat()
            }).execute()
            
            # Combine results
            stats = {
                'sensor_counts': sensor_result.data if sensor_result.data else [],
                'alert_counts': alert_result.data if alert_result.data else [],
                'time_range': f"Last {hours} hours",
                'generated_at': datetime.now().isoformat()
            }
            
            return stats
            
        except Exception as e:
            print(f"❌ Error getting device statistics: {e}")
            return {}
    
    def get_recent_alerts(self, limit=10):
        """
        Get most recent alerts across all devices
        """
        if not self.supabase:
            return []
        
        try:
            result = self.supabase.table('alert_history')\
                .select('*')\
                .order('timestamp', desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            print(f"❌ Error getting recent alerts: {e}")
            return []
    
    def cleanup_old_data(self, days_to_keep=30):
        """
        Clean up old data to manage database size
        Keep only recent data for performance
        """
        if not self.supabase:
            return False
        
        try:
            # Calculate cutoff date
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            # Delete old sensor readings
            sensor_result = self.supabase.table('sensor_readings')\
                .delete()\
                .lt('timestamp', cutoff_date.isoformat())\
                .execute()
            
            # Delete old alerts
            alert_result = self.supabase.table('alert_history')\
                .delete()\
                .lt('timestamp', cutoff_date.isoformat())\
                .execute()
            
            print(f"🧹 Cleaned up data older than {days_to_keep} days")
            return True
            
        except Exception as e:
            print(f"❌ Error cleaning up old data: {e}")
            return False

def create_database_schema():
    """
    SQL script to create the required database tables
    Run this in Supabase SQL Editor
    """
    
    schema_sql = """
    -- Create sensor readings table for time-series data
    CREATE TABLE IF NOT EXISTS sensor_readings (
        id BIGSERIAL PRIMARY KEY,
        device_name VARCHAR(50) NOT NULL,
        timestamp TIMESTAMPTZ NOT NULL,
        current_amps DECIMAL(5,2),
        temperature_celsius DECIMAL(5,2), 
        pressure_bar DECIMAL(5,2),
        created_at TIMESTAMPTZ DEFAULT NOW()
    );

    -- Create alert history table
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

    -- Create indexes for better query performance
    CREATE INDEX IF NOT EXISTS idx_sensor_readings_device_time 
        ON sensor_readings(device_name, timestamp);
    
    CREATE INDEX IF NOT EXISTS idx_sensor_readings_timestamp 
        ON sensor_readings(timestamp);
    
    CREATE INDEX IF NOT EXISTS idx_alert_history_device_time 
        ON alert_history(device_name, timestamp);
    
    CREATE INDEX IF NOT EXISTS idx_alert_history_severity 
        ON alert_history(severity, timestamp);

    -- Create helper functions for statistics
    CREATE OR REPLACE FUNCTION get_device_sensor_counts(start_time TIMESTAMPTZ, end_time TIMESTAMPTZ)
    RETURNS TABLE(device_name VARCHAR, sensor_count BIGINT) AS $$
    BEGIN
        RETURN QUERY
        SELECT sr.device_name, COUNT(*) as sensor_count
        FROM sensor_readings sr
        WHERE sr.timestamp BETWEEN start_time AND end_time
        GROUP BY sr.device_name
        ORDER BY sensor_count DESC;
    END;
    $$ LANGUAGE plpgsql;

    CREATE OR REPLACE FUNCTION get_device_alert_counts(start_time TIMESTAMPTZ, end_time TIMESTAMPTZ)
    RETURNS TABLE(device_name VARCHAR, alert_count BIGINT) AS $$
    BEGIN
        RETURN QUERY
        SELECT ah.device_name, COUNT(*) as alert_count
        FROM alert_history ah
        WHERE ah.timestamp BETWEEN start_time AND end_time
        GROUP BY ah.device_name
        ORDER BY alert_count DESC;
    END;
    $$ LANGUAGE plpgsql;
    """
    
    return schema_sql

# Test function
def test_database_connection():
    """
    Test the database connection and basic operations
    """
    print("🧪 Testing Supabase Database Connection...")
    
    try:
        db = SupabaseManager()
        
        if db.supabase:
            print("✅ Database connection test passed!")
            
            # Test saving a sample sensor reading
            sample_sensor_data = {
                'device_name': 'TestDevice_001',
                'timestamp': datetime.now().isoformat(),
                'sensors': {
                    'current_amps': 12.5,
                    'temperature_celsius': 75.0,
                    'pressure_bar': 2.1
                }
            }
            
            success = db.save_sensor_reading(sample_sensor_data)
            if success:
                print("✅ Sample sensor data saved successfully!")
            else:
                print("❌ Failed to save sample sensor data")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")

if __name__ == "__main__":
    # Print the schema SQL for manual setup
    print("📋 Database Schema SQL (copy to Supabase SQL Editor):")
    print("=" * 60)
    print(create_database_schema())
    print("=" * 60)
    
    # Test connection
    test_database_connection()
