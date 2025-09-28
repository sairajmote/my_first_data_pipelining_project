import React, { useState, useEffect } from 'react';
import { supabase, TABLES } from './config/supabase';
import StatsOverview from './components/StatsOverview';
import SensorChart from './components/SensorChart';
import DeviceCard from './components/DeviceCard';
import AlertPanel from './components/AlertPanel';
import { RefreshCw, Zap } from 'lucide-react';

function App() {
  const [devices, setDevices] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [error, setError] = useState(null);

  // Generate demo data while database is being fixed
  const generateDemoData = () => {
    const demoDevices = [];
    for (let i = 1; i <= 20; i++) {
      const current = parseFloat((Math.random() * 15 + 5).toFixed(2));
      const temp = parseFloat((Math.random() * 70 + 20).toFixed(2));
      const pressure = parseFloat((Math.random() * 2 + 1).toFixed(2));
      
      demoDevices.push({
        device_id: i,
        device_name: `EnergyDevice_${i.toString().padStart(3, '0')}`,
        timestamp: new Date().toISOString(),
        current_amps: current,
        temperature_celsius: temp,
        pressure_bar: pressure,
        sensors: {
          current_amps: current,
          temperature_celsius: temp,
          pressure_bar: pressure
        }
      });
    }
    return demoDevices;
  };

  // Fetch latest sensor readings for all devices
  const fetchDeviceData = async () => {
    try {
      setError(null);
      console.log('🔄 Fetching device data from Supabase...');
      
      // Try to fetch real data from Supabase
      const { data: sensorData, error: sensorError } = await supabase
        .from(TABLES.SENSOR_READINGS)
        .select('*')
        .order('timestamp', { ascending: false })
        .limit(500);

      console.log('📊 Supabase response:', { sensorData, sensorError });

      if (sensorError) {
        console.error('Error fetching sensor data:', sensorError);
        setError(`Database error: ${sensorError.message}`);
        return;
      }

      if (sensorData && sensorData.length > 0) {
        // Group by device_name to get latest reading per device
        const deviceMap = new Map();
        sensorData.forEach(reading => {
          if (!deviceMap.has(reading.device_name) || 
              new Date(reading.timestamp) > new Date(deviceMap.get(reading.device_name).timestamp)) {
            // Add device_id for compatibility
            reading.device_id = reading.device_name;
            deviceMap.set(reading.device_name, reading);
          }
        });

        const realDevices = Array.from(deviceMap.values());
        setDevices(realDevices);
        setLastUpdate(new Date());
        console.log(`✅ Loaded ${realDevices.length} devices from database`);
        console.log('Sample device:', realDevices[0]);
      } else {
        // Try to get sensor data from alerts table as fallback
        console.log('No sensor_readings found, checking alerts for sensor data...');
        const { data: alertData } = await supabase
          .from(TABLES.ALERTS)
          .select('*')
          .eq('alert_type', 'SENSOR_DATA')
          .order('timestamp', { ascending: false })
          .limit(100);

        if (alertData && alertData.length > 0) {
          // Convert alerts back to device format
          const deviceMap = new Map();
          alertData.forEach(alert => {
            if (!deviceMap.has(alert.device_name)) {
              // Parse sensor data from alert message
              const match = alert.message.match(/(\d+\.?\d*)A, (\d+\.?\d*)°C/);
              if (match) {
                const device = {
                  device_id: alert.device_name,
                  device_name: alert.device_name,
                  timestamp: alert.timestamp,
                  current_amps: parseFloat(match[1]),
                  temperature_celsius: parseFloat(match[2]),
                  pressure_bar: 2.0 // Default value
                };
                deviceMap.set(alert.device_name, device);
              }
            }
          });
          
          if (deviceMap.size > 0) {
            setDevices(Array.from(deviceMap.values()));
            setError('Using sensor data from alerts (sensor_readings table issue)');
            setLastUpdate(new Date());
            console.log(`✅ Loaded ${deviceMap.size} devices from alerts`);
          } else {
            // No sensor data from alerts fallback
            setDevices([]);
            setError('No sensor data found in database or alerts');
            setLastUpdate(new Date());
          }
        } else {
          // No sensor data found
          setDevices([]);
          setError('No sensor data found in database');
          setLastUpdate(new Date());
        }
      }
      
    } catch (err) {
      console.error('Error in fetchDeviceData:', err);
      setError('Failed to connect to database');
    }
  };

  // Generate demo alerts
  const generateDemoAlerts = () => {
    const alertTypes = ['HIGH_CURRENT', 'HIGH_TEMPERATURE', 'HIGH_PRESSURE'];
    const severities = ['warning', 'critical'];
    const demoAlerts = [];
    
    for (let i = 0; i < 8; i++) {
      const alertType = alertTypes[Math.floor(Math.random() * alertTypes.length)];
      const severity = severities[Math.floor(Math.random() * severities.length)];
      
      demoAlerts.push({
        device_name: `EnergyDevice_${Math.floor(Math.random() * 20 + 1).toString().padStart(3, '0')}`,
        alert_type: alertType,
        message: `${alertType.replace('_', ' ').toLowerCase()} detected`,
        severity: severity,
        sensor_value: Math.random() * 100,
        timestamp: new Date(Date.now() - Math.random() * 3600000).toISOString()
      });
    }
    
    return demoAlerts;
  };

  // Fetch recent alerts
  const fetchAlerts = async () => {
    try {
      // Try to fetch real alerts from Supabase
      const { data: alertData, error: alertError } = await supabase
        .from(TABLES.ALERTS)
        .select('*')
        .order('timestamp', { ascending: false })
        .limit(50);

      if (alertError) {
        console.error('Error fetching alerts:', alertError);
        setAlerts([]);
        return;
      }

      if (alertData && alertData.length > 0) {
        setAlerts(alertData);
        console.log(`✅ Loaded ${alertData.length} real alerts`);
      } else {
        // No alerts in database
        setAlerts([]);
        console.log('No alerts found in database');
      }
    } catch (err) {
      console.error('Error in fetchAlerts:', err);
      setAlerts([]);
    }
  };

  // Initial data fetch
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchDeviceData(), fetchAlerts()]);
      setLoading(false);
    };

    loadData();
  }, []);

  // Set up real-time updates every 5 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      fetchDeviceData();
      fetchAlerts();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  // Manual refresh
  const handleRefresh = async () => {
    setLoading(true);
    console.log('🔄 Manual refresh triggered - clearing cache');
    setDevices([]);
    setAlerts([]);
    await Promise.all([fetchDeviceData(), fetchAlerts()]);
    setLoading(false);
  };

  if (loading && devices.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 text-blue-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <Zap className="w-8 h-8 text-blue-600" />
              <div>
                <h1 className="text-xl font-bold text-gray-900">
                  IoT Energy Management
                </h1>
                <p className="text-sm text-gray-500">Real-time monitoring dashboard</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              {lastUpdate && (
                <span className="text-sm text-gray-500">
                  Last update: {lastUpdate.toLocaleTimeString()}
                </span>
              )}
              <button
                onClick={handleRefresh}
                disabled={loading}
                className="flex items-center space-x-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                <span>Refresh</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Stats Overview */}
        <StatsOverview devices={devices} alerts={alerts} />

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <SensorChart
            data={devices}
            title="Current Consumption"
            dataKey="current_amps"
            color="#3b82f6"
            unit="A"
            threshold={15}
          />
          <SensorChart
            data={devices}
            title="Temperature"
            dataKey="temperature_celsius"
            color="#f59e0b"
            unit="°C"
            threshold={80}
          />
          <SensorChart
            data={devices}
            title="Pressure"
            dataKey="pressure_bar"
            color="#8b5cf6"
            unit="bar"
            threshold={2.5}
          />
        </div>

        {/* Devices and Alerts */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Device Grid */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-md p-4 mb-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">
                Device Status ({devices.length} devices)
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 max-h-96 overflow-y-auto">
                {devices.map((device) => (
                  <DeviceCard
                    key={device.device_id}
                    device={device}
                    isOnline={true}
                  />
                ))}
              </div>
            </div>
          </div>

          {/* Alerts Panel */}
          <div className="lg:col-span-1">
            <AlertPanel alerts={alerts} />
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
