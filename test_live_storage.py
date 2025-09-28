"""
Test live data storage with your Supabase tables
"""

from working_data_processor import RestSupabaseClient
from datetime import datetime

def test_live_storage():
    print('🧪 Testing data storage with your Supabase tables...')

    client = RestSupabaseClient()

    # Test sensor data that will trigger alerts
    test_data = {
        'device_name': 'EnergyDevice_LIVE_TEST',
        'timestamp': datetime.now().isoformat(),
        'sensors': {
            'current_amps': 17.5,  # Above 15A threshold
            'temperature_celsius': 85.0,  # Above 80°C threshold  
            'pressure_bar': 2.8  # Above 2.5 bar threshold
        }
    }

    print('📤 Storing sensor data...')
    sensor_result = client.store_sensor_data(test_data)
    print(f'Sensor storage: {"✅ SUCCESS" if sensor_result else "❌ FAILED"}')

    # Test alert storage
    test_alert = {
        'device_name': 'EnergyDevice_LIVE_TEST',
        'alert_type': 'HIGH_CURRENT',
        'severity': 'critical',
        'message': 'Critical: High current detected - 17.5A (limit: 15.0A)',
        'value': 17.5,
        'threshold': 15.0,
        'timestamp': datetime.now().isoformat()
    }

    print('🚨 Storing alert...')
    alert_result = client.store_alert(test_alert)
    print(f'Alert storage: {"✅ SUCCESS" if alert_result else "❌ FAILED"}')

    if sensor_result and alert_result:
        print('\n🎉 SUCCESS! Data storage is working perfectly!')
        print('✅ Refresh your Supabase dashboard to see the new data')
        print('✅ Refresh your React dashboard to see real-time updates')
        return True
    else:
        print('\n❌ Some issues detected. Check the error messages above.')
        return False

if __name__ == "__main__":
    test_live_storage()
