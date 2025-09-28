# IoT Energy Management System

A step-by-step IoT system that simulates energy monitoring devices and processes their data in real-time.

## 🎯 What This Does

This system simulates multiple energy monitoring devices (like smart meters in a factory) that:
- Measure electrical current (Amps)
- Monitor temperature (°C) 
- Track pressure (Bar)
- Send alerts when readings are dangerous

## 📁 Project Structure

```
naya project/
├── iot_device_simulator.py    # Main script - creates fake IoT devices
├── requirements.txt           # Python packages needed
├── .env                      # Configuration settings (your actual values)
├── .env.example             # Template for configuration
└── README.md               # This file
```

## 🚀 Step 1: Simulated IoT Devices (CURRENT STEP)

We've created the first part - simulated IoT devices that generate realistic sensor data.

### How to Run

1. **Install Python packages:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the simulator:**
   ```bash
   python iot_device_simulator.py
   ```

3. **What you'll see:**
   - 5 simulated devices generating data every 3 seconds
   - Current, temperature, and pressure readings
   - Automatic alerts when readings exceed safe limits
   - Press Ctrl+C to stop

### Configuration

You can change settings in the `.env` file:
- `DEVICE_COUNT`: How many devices to simulate (default: 5)
- `SIMULATION_INTERVAL`: Seconds between readings (default: 3)
- `CURRENT_ALERT_THRESHOLD`: Alert when current exceeds this (default: 15A)
- `TEMPERATURE_ALERT_THRESHOLD`: Alert when temp exceeds this (default: 80°C)
- `PRESSURE_ALERT_THRESHOLD`: Alert when pressure exceeds this (default: 2.5 bar)

## 🔄 Next Steps

1. ✅ **Simulated IoT Devices** (COMPLETED)
2. ⏳ **Data Streaming Layer** (Kafka setup)
3. ⏳ **Data Processing** (Alert system)
4. ⏳ **Storage Layer** (Database)
5. ⏳ **Visualization** (Dashboard)
6. ⏳ **Control Layer** (Device commands)

## 🛠️ Technologies Used

- **Python**: Main programming language
- **python-dotenv**: For configuration management
- **Random & Time**: For realistic data simulation

---

*This is a learning project built step-by-step to understand IoT systems and real-time data processing.*
