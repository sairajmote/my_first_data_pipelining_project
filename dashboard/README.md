# IoT Energy Management Dashboard

A modern React dashboard for monitoring IoT energy devices in real-time.

## 🚀 Features

- **Real-time monitoring** of 100+ IoT devices
- **Interactive charts** showing current, temperature, and pressure trends
- **Alert system** with severity levels and real-time notifications
- **Device status overview** with online/offline indicators
- **Responsive design** that works on desktop and mobile
- **Auto-refresh** every 5 seconds for live data

## 🛠️ Technologies

- **React 18** - Modern React with hooks
- **Tailwind CSS** - Utility-first CSS framework
- **Recharts** - Responsive chart library
- **Supabase** - Real-time database integration
- **Lucide React** - Beautiful icons

## 📊 Dashboard Components

### Stats Overview
- Total devices count
- Online devices status
- Active alerts counter
- Average sensor readings

### Real-time Charts
- **Current Consumption** - Line chart with 15A threshold
- **Temperature Monitoring** - Line chart with 80°C threshold  
- **Pressure Tracking** - Line chart with 2.5 bar threshold

### Device Cards
- Individual device status
- Current sensor readings
- Alert indicators
- Last update timestamps

### Alert Panel
- Recent alerts with severity levels
- Color-coded notifications
- Timestamp tracking
- Alert history

## 🚀 Getting Started

1. **Install dependencies:**
   ```bash
   cd dashboard
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm start
   ```

3. **Open your browser:**
   Navigate to `http://localhost:3000`

## 📡 Data Integration

The dashboard connects to your Supabase database and expects these tables:
- `sensor_readings` - Device sensor data
- `alerts` - Alert history and notifications

Data is automatically refreshed every 5 seconds for real-time monitoring.

## 🎨 Customization

- **Colors**: Modify `tailwind.config.js` for custom color schemes
- **Charts**: Update chart configurations in `SensorChart.js`
- **Thresholds**: Adjust alert thresholds in component props
- **Refresh Rate**: Change auto-refresh interval in `App.js`

## 📱 Responsive Design

The dashboard is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones

## 🔧 Configuration

The dashboard uses your existing Supabase configuration from the main project's `.env` file.

---

*Part of the IoT Energy Management System - Step 5: Visualization Layer*
