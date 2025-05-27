import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import SensorGrid from '../components/SensorGrid';
import HistoryChart from '../components/HistoryChart';
import SettingsForm from '../components/SettingsForm';

import { FaSignOutAlt, FaEdit } from 'react-icons/fa';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

export default function Dashboard() {
  const [sensors, setSensors] = useState({});
  const [settings, setSettings] = useState(null);
  const [statusMap, setStatusMap] = useState({});
  const [chartData, setChartData] = useState(null);
  const [fromTime, setFromTime] = useState('');
  const [toTime, setToTime] = useState('');
  const [showSettings, setShowSettings] = useState(false);

  const { token, logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!token) return;

    const fetchLive = async () => {
      try {
        const [sensorRes, settingsRes] = await Promise.all([
          api.get('/sensors/', { headers: { Authorization: `Bearer ${token}` } }),
          api.get('/settings/', { headers: { Authorization: `Bearer ${token}` } }),
        ]);

        const latest = sensorRes.data[0];
        const userSettings = settingsRes.data;

        setSensors(latest);
        setSettings(userSettings);
        setStatusMap(evaluateStatus(latest, userSettings));
      } catch (err) {
        console.error('Live data error:', err);
        toast.error('Failed to load live data.');
      }
    };

    fetchLive();
  }, [token]);

  const fetchHistory = async () => {
    if (!fromTime || !toTime || !token) return;

    try {
      const res = await api.get('/sensors/history', {
        params: {
          from: new Date(fromTime).toISOString(),
          to: new Date(toTime).toISOString(),
        },
        headers: { Authorization: `Bearer ${token}` },
      });

      const data = res.data;
      const labels = data.map(d => new Date(d.timestamp));
      const extract = key => data.map(d => d[key]);

      setChartData({
        labels,
        datasets: [
          { label: 'Temperature (°C)', data: extract('temp'), borderColor: 'rgb(255, 99, 132)', fill: false },
          { label: 'Humidity (%)', data: extract('hum'), borderColor: 'rgb(54, 162, 235)', fill: false },
          { label: 'Light (lx)', data: extract('light'), borderColor: 'rgb(255, 206, 86)', fill: false },
          { label: 'Soil Moisture', data: extract('soil'), borderColor: 'rgb(75, 192, 192)', fill: false },
        ],
      });
    } catch (err) {
      console.error('History fetch failed:', err);
      toast.error('Failed to load history data.');
    }
  };

  const evaluateStatus = (sensor, s) => {
    if (!sensor || !s) return {};
    return {
      temp: sensor.temp > s.temp_max || sensor.temp < s.temp_min ? 'danger' : 'ok',
      hum: sensor.hum < s.hum_min || sensor.hum > s.hum_max ? 'warning' : 'ok',
      soil: sensor.soil < s.soil_min ? 'danger' :
        sensor.soil > s.soil_min + 100 ? 'ok' : 'warning',
      light: sensor.light < s.light_min || sensor.light > s.light_max ? 'warning' : 'ok',
      motion: sensor.motion ? 'alert' : 'ok',
      acc_x: 'ok', acc_y: 'ok', acc_z: 'ok', dist: 'ok'
    };
  };

  const handleLogout = async () => {
    try {
      await api.post('/logout', {}, { headers: { Authorization: `Bearer ${token}` } });
      toast.success('Logged out successfully');
    } catch (err) {
      toast.error('Logout failed or already logged out');
    } finally {
      logout();
      navigate('/login');
    }
  };

  return (
    <div className="p-6 space-y-10 relative">
      <ToastContainer position="top-right" autoClose={3000} />

      {/* Top right action buttons */}
      <div className="absolute top-6 right-6 flex gap-3 z-10">
        <button
          onClick={() => setShowSettings(true)}
          className="bg-green-600 text-white px-4 py-2 rounded shadow flex items-center gap-2"
        >
          <FaEdit /> Edit
        </button>
        <button
          onClick={handleLogout}
          className="bg-red-500 text-white px-4 py-2 rounded shadow flex items-center gap-2"
        >
          <FaSignOutAlt /> Logout
        </button>
      </div>

      <h1 className="text-3xl font-semibold mb-4">Live Sensor Data</h1>

      <SensorGrid sensors={sensors} statusMap={statusMap} />
      <HistoryChart
        fromTime={fromTime}
        toTime={toTime}
        setFromTime={setFromTime}
        setToTime={setToTime}
        fetchHistory={fetchHistory}
        chartData={chartData}
      />

      {showSettings && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
          <div className="bg-white p-6 rounded shadow max-w-2xl w-full relative">
            <button
              onClick={() => setShowSettings(false)}
              className="absolute top-2 right-2 text-gray-600 hover:text-black text-xl"
            >
              ×
            </button>
            <SettingsForm initialData={settings} onClose={() => setShowSettings(false)} />
          </div>
        </div>
      )}
    </div>
  );
}
