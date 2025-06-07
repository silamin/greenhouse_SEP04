import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { toast } from 'react-toastify';
import { FaSave } from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';
import 'react-toastify/dist/ReactToastify.css';

export default function SettingsForm({ initialData = null, onClose = null }) {
  const [settings, setSettings] = useState({
    owner: '',
    name: '',
    temp_min: '',
    temp_max: '',
    hum_min: '',
    hum_max: '',
    light_min: '',
    light_max: '',
    soil_min: '',
  });

  const { token } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (initialData) {
      setSettings(initialData);
    } else if (token) {
      api.get('/settings', {
        headers: { Authorization: `Bearer ${token}` }
      })
      .then(res => setSettings(res.data))
      .catch(err => {
        console.error('Failed to fetch settings:', err);
        toast.error('Failed to fetch settings');
      });
    }
  }, [token, initialData]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setSettings(prev => ({ ...prev, [name]: value }));
  };

const handleSubmit = (e) => {
  e.preventDefault();

  api.post('/settings', settings, {
    headers: { Authorization: `Bearer ${token}` }
  })
  .then(() => {
    toast.success('Settings saved successfully');
    
    if (onClose) {
      onClose(); // Only close the modal
    } else {
      navigate('/'); // If not in a modal, redirect to dashboard
    }
  })
  .catch(err => {
    console.error('Failed to save settings:', err);
    toast.error('Failed to save settings');
  });
};


  return (
    <form onSubmit={handleSubmit} className="w-full bg-white p-6 rounded shadow max-w-2xl grid grid-cols-1 gap-4 md:grid-cols-2">
      {[
        { label: 'Name', name: 'name', type: 'text' },
        { label: 'Temp Min (°C)', name: 'temp_min', type: 'number' },
        { label: 'Temp Max (°C)', name: 'temp_max', type: 'number' },
        { label: 'Humidity Min (%)', name: 'hum_min', type: 'number' },
        { label: 'Humidity Max (%)', name: 'hum_max', type: 'number' },
        { label: 'Light Min', name: 'light_min', type: 'number' },
        { label: 'Light Max', name: 'light_max', type: 'number' },
        { label: 'Soil Moisture Min', name: 'soil_min', type: 'number' },
      ].map(({ label, name, type }) => (
        <label key={name} className="block">
          <span className="text-gray-700">{label}</span>
          <input
            type={type}
            name={name}
            value={settings[name] || ''}
            onChange={handleChange}
            className="mt-1 block w-full px-3 py-2 border rounded"
            required
          />
        </label>
      ))}

      <div className="md:col-span-2">
        <button
          type="submit"
          className="w-full bg-green-500 text-white py-2 px-6 rounded flex items-center gap-2 justify-center"
        >
          <FaSave /> Save Settings
        </button>
      </div>
    </form>
  );
}
