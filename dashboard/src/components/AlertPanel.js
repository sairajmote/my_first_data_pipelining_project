import React from 'react';
import { AlertTriangle, AlertCircle, Info, CheckCircle } from 'lucide-react';

const AlertPanel = ({ alerts = [] }) => {
  const getAlertIcon = (severity) => {
    const severityLower = severity?.toLowerCase() || '';
    switch (severityLower) {
      case 'critical':
      case 'emergency':
        return <AlertTriangle className="w-5 h-5 text-red-500" />;
      case 'warning':
        return <AlertCircle className="w-5 h-5 text-yellow-500" />;
      case 'info':
        return <Info className="w-5 h-5 text-blue-500" />;
      default:
        return <AlertCircle className="w-5 h-5 text-yellow-500" />; // Default to warning
    }
  };

  const getAlertBgColor = (severity) => {
    const severityLower = severity?.toLowerCase() || '';
    switch (severityLower) {
      case 'critical':
      case 'emergency':
        return 'bg-red-50 border-red-200';
      case 'warning':
        return 'bg-yellow-50 border-yellow-200';
      case 'info':
        return 'bg-blue-50 border-blue-200';
      default:
        return 'bg-yellow-50 border-yellow-200'; // Default to warning color
    }
  };

  const getAlertTextColor = (severity) => {
    const severityLower = severity?.toLowerCase() || '';
    switch (severityLower) {
      case 'critical':
      case 'emergency':
        return 'text-red-800';
      case 'warning':
        return 'text-yellow-800';
      case 'info':
        return 'text-blue-800';
      default:
        return 'text-yellow-800'; // Default to warning color
    }
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  // Sort alerts by timestamp (newest first)
  const sortedAlerts = [...alerts].sort((a, b) => 
    new Date(b.timestamp) - new Date(a.timestamp)
  ).slice(0, 10); // Show only last 10 alerts

  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-800">Recent Alerts</h3>
      </div>

      <div className="space-y-3 max-h-96 overflow-y-auto">
        {sortedAlerts.length === 0 ? (
          <div className="text-center py-8">
            <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-3" />
            <p className="text-gray-500">No alerts at this time</p>
            <p className="text-sm text-gray-400">All systems operating normally</p>
          </div>
        ) : (
          sortedAlerts.map((alert, index) => (
            <div
              key={index}
              className={`p-3 rounded-lg border ${getAlertBgColor(alert.severity)}`}
            >
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 mt-0.5">
                  {getAlertIcon(alert.severity)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <p className={`text-sm font-medium ${getAlertTextColor(alert.severity)}`}>
                      {alert.device_name}
                    </p>
                    <span className="text-xs text-gray-500">
                      {formatTime(alert.timestamp)}
                    </span>
                  </div>
                  <p className={`text-sm mt-1 ${getAlertTextColor(alert.severity)}`}>
                    {alert.message}
                  </p>
                  {alert.sensor_value && (
                    <p className="text-xs text-gray-600 mt-1">
                      Value: {alert.sensor_value} {alert.unit}
                    </p>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default AlertPanel;
