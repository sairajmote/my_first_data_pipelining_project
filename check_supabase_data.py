"""
Check if data is being stored in Supabase
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

def check_data():
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    headers = {
        'apikey': key,
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json'
    }

    print('📊 Checking Supabase data...')
    
    # Check sensor_readings
    print('\n📊 Sensor readings:')
    try:
        response = requests.get(
            f'{url}/rest/v1/sensor_readings?limit=5&order=timestamp.desc',
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f'Found {len(data)} sensor readings')
            for reading in data[:3]:
                print(f'  - {reading.get("device_name")}: {reading.get("current_amps")}A, {reading.get("temperature_celsius")}°C')
        else:
            print(f'Error: {response.status_code} - {response.text}')
    except Exception as e:
        print(f'Exception: {e}')

    # Check alerts
    print('\n🚨 Alerts:')
    try:
        response = requests.get(
            f'{url}/rest/v1/alerts?limit=5&order=timestamp.desc',
            headers=headers
        )
        
        if response.status_code == 200:
            alerts = response.json()
            print(f'Found {len(alerts)} alerts')
            for alert in alerts[:3]:
                print(f'  - {alert.get("device_name")}: {alert.get("alert_type")} ({alert.get("severity")})')
        else:
            print(f'Error: {response.status_code} - {response.text}')
    except Exception as e:
        print(f'Exception: {e}')

if __name__ == "__main__":
    check_data()
