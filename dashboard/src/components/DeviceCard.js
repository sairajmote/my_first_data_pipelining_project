import React from 'react';
import { Activity, Thermometer, Gauge, AlertTriangle, CheckCircle } from 'lucide-react';

const DeviceCard = ({ device, isOnline = true }) => {
  const { device_name, sensors, timestamp } = device;
  
  // Handle both direct properties and nested sensors object
  const current_amps = device.current_amps || sensors?.current_amps || 0;
  const temperature_celsius = device.temperature_celsius || sensors?.temperature_celsius || 0;
  const pressure_bar = device.pressure_bar || sensors?.pressure_bar || 0;

  // Determine alert status based on thresholds
  const hasCurrentAlert = current_amps > 15;
  const hasTempAlert = temperature_celsius > 80;
  const hasPressureAlert = pressure_bar > 2.5;
  const hasAnyAlert = hasCurrentAlert || hasTempAlert || hasPressureAlert;

  const formatTime = (timestamp) => {
    if (!timestamp) return 'No data';
    return new Date(timestamp).toLocaleTimeString();
  };

  return (
    <div className={`bg-white rounded-lg shadow-md p-4 border-l-4 ${
      hasAnyAlert ? 'border-l-red-500' : 'border-l-green-500'
    }`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <div className={`w-3 h-3 rounded-full ${
            isOnline ? 'bg-green-500' : 'bg-gray-400'
          }`}></div>
          <h3 className="font-semibold text-gray-800">{device_name}</h3>
        </div>
        {hasAnyAlert ? (
          <AlertTriangle className="w-5 h-5 text-red-500" />
        ) : (
          <CheckCircle className="w-5 h-5 text-green-500" />
        )}
      </div>

      {/* Sensor Readings */}
      <div className="space-y-2">
        {/* Current */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Activity className="w-4 h-4 text-blue-500" />
            <span className="text-sm text-gray-600">Current</span>
          </div>
          <span className={`font-medium ${
            hasCurrentAlert ? 'text-red-600' : 'text-gray-800'
          }`}>
            {current_amps?.toFixed(1) || '0.0'}A
          </span>
        </div>

        {/* Temperature */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Thermometer className="w-4 h-4 text-orange-500" />
            <span className="text-sm text-gray-600">Temperature</span>
          </div>
          <span className={`font-medium ${
            hasTempAlert ? 'text-red-600' : 'text-gray-800'
          }`}>
            {temperature_celsius?.toFixed(1) || '0.0'}°C
          </span>
        </div>

        {/* Pressure */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Gauge className="w-4 h-4 text-purple-500" />
            <span className="text-sm text-gray-600">Pressure</span>
          </div>
          <span className={`font-medium ${
            hasPressureAlert ? 'text-red-600' : 'text-gray-800'
          }`}>
            {pressure_bar?.toFixed(1) || '0.0'} bar
          </span>
        </div>
      </div>

      {/* Timestamp */}
      <div className="mt-3 pt-2 border-t border-gray-100">
        <span className="text-xs text-gray-500">
          Last update: {formatTime(timestamp)}
        </span>
      </div>
    </div>
  );
};

export default DeviceCard;
