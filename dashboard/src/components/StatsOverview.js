import React from 'react';
import { Activity, Thermometer, Gauge, AlertTriangle } from 'lucide-react';

const StatsOverview = ({ devices = [], alerts = [] }) => {
  // Calculate statistics
  const totalDevices = devices.length;
  const onlineDevices = devices.filter(device => {
    // Consider device online if last reading was within 30 seconds
    const lastReading = new Date(device.timestamp);
    const now = new Date();
    return (now - lastReading) < 30000;
  }).length;

  // Removed active alerts calculation - not needed


  // Calculate average values from all devices
  const avgCurrent = devices.length > 0 
    ? devices.reduce((sum, device) => sum + (device.current_amps || device.sensors?.current_amps || 0), 0) / devices.length
    : 0;

  const avgTemperature = devices.length > 0
    ? devices.reduce((sum, device) => sum + (device.temperature_celsius || device.sensors?.temperature_celsius || 0), 0) / devices.length
    : 0;

  const avgPressure = devices.length > 0
    ? devices.reduce((sum, device) => sum + (device.pressure_bar || device.sensors?.pressure_bar || 0), 0) / devices.length
    : 0;

  const StatCard = ({ title, value, unit, icon: Icon, color, bgColor }) => (
    <div className="bg-white rounded-lg shadow-md p-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600 mb-1">{title}</p>
          <p className="text-2xl font-bold text-gray-800">
            {value}
            {unit && <span className="text-lg text-gray-500 ml-1">{unit}</span>}
          </p>
        </div>
        <div className={`p-3 rounded-full ${bgColor}`}>
          <Icon className={`w-6 h-6 ${color}`} />
        </div>
      </div>
    </div>
  );

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5 gap-4 mb-6">
      <StatCard
        title="Total Devices"
        value={totalDevices}
        icon={Activity}
        color="text-blue-600"
        bgColor="bg-blue-100"
      />
      
      <StatCard
        title="Online Devices"
        value={onlineDevices}
        icon={Activity}
        color="text-green-600"
        bgColor="bg-green-100"
      />
      
      <StatCard
        title="Avg Current"
        value={avgCurrent.toFixed(1)}
        unit="A"
        icon={Activity}
        color="text-blue-600"
        bgColor="bg-blue-100"
      />
      
      <StatCard
        title="Avg Temperature"
        value={avgTemperature.toFixed(1)}
        unit="°C"
        icon={Thermometer}
        color="text-orange-600"
        bgColor="bg-orange-100"
      />
      
      <StatCard
        title="Avg Pressure"
        value={avgPressure.toFixed(1)}
        unit="bar"
        icon={Gauge}
        color="text-purple-600"
        bgColor="bg-purple-100"
      />
    </div>
  );
};

export default StatsOverview;
