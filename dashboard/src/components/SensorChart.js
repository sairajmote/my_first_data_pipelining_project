import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const SensorChart = ({ data, title, dataKey, color, unit, threshold }) => {
  // Format data for chart
  const chartData = data.map(item => ({
    time: new Date(item.timestamp).toLocaleTimeString(),
    value: item[dataKey] || item.sensors?.[dataKey] || 0,
    timestamp: item.timestamp
  })).slice(-20); // Show last 20 data points

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0];
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="text-sm text-gray-600">{`Time: ${label}`}</p>
          <p className="text-sm font-medium" style={{ color: data.color }}>
            {`${title}: ${data.value?.toFixed(1)} ${unit}`}
          </p>
          {threshold && data.value > threshold && (
            <p className="text-xs text-red-500 mt-1">⚠️ Above threshold ({threshold} {unit})</p>
          )}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-800">{title}</h3>
        <span className="text-sm text-gray-500">Last 20 readings</span>
      </div>
      
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis 
              dataKey="time" 
              tick={{ fontSize: 12 }}
              stroke="#666"
            />
            <YAxis 
              tick={{ fontSize: 12 }}
              stroke="#666"
              label={{ value: unit, angle: -90, position: 'insideLeft' }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Line 
              type="monotone" 
              dataKey="value" 
              stroke={color} 
              strokeWidth={2}
              dot={{ fill: color, strokeWidth: 2, r: 3 }}
              activeDot={{ r: 5, stroke: color, strokeWidth: 2 }}
            />
            {threshold && (
              <Line 
                type="monotone" 
                dataKey={() => threshold}
                stroke="#ef4444" 
                strokeWidth={1}
                strokeDasharray="5 5"
                dot={false}
                activeDot={false}
              />
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>
      
      {threshold && (
        <div className="mt-2 text-xs text-gray-500">
          <span className="inline-block w-3 h-0.5 bg-red-500 mr-2"></span>
          Alert threshold: {threshold} {unit}
        </div>
      )}
    </div>
  );
};

export default SensorChart;
