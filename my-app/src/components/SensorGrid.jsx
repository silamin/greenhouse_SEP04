import React from 'react';
import {
  MdThermostat,
  MdWaterDrop,
  MdYard,
  MdLightMode,
  MdStraighten,
  MdMotionPhotosOn,
  MdOutlineSwipe,
} from 'react-icons/md';

export default function SensorGrid({ sensors, statusMap }) {
  const sensorItems = [
    { key: 'temp', label: 'Temperature', unit: '°C', icon: <MdThermostat /> },
    { key: 'hum', label: 'Humidity', unit: '%', icon: <MdWaterDrop /> },
    { key: 'soil', label: 'Soil Moisture', unit: '', icon: <MdYard /> },
    { key: 'light', label: 'Light', unit: 'lx', icon: <MdLightMode /> },
    { key: 'dist', label: 'Distance', unit: 'cm', icon: <MdStraighten /> },
    { key: 'motion', label: 'Motion', unit: '', icon: <MdMotionPhotosOn /> },
    { key: 'acc_x', label: 'Acc X', unit: '', icon: <MdOutlineSwipe /> },
    { key: 'acc_y', label: 'Acc Y', unit: '', icon: <MdOutlineSwipe /> },
    { key: 'acc_z', label: 'Acc Z', unit: '', icon: <MdOutlineSwipe /> },
  ];

  const getColor = (status) => {
    switch (status) {
      case 'danger': return 'bg-red-500';
      case 'warning': return 'bg-yellow-400';
      case 'alert': return 'bg-purple-600 animate-pulse';
      default: return 'bg-green-500';
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {sensorItems.map(({ key, label, unit, icon }) => (
        <div key={key} className="bg-white shadow rounded p-4 border border-gray-200">
          <div className="flex justify-between items-center mb-2">
            <div className="flex items-center gap-2 text-lg font-bold">
              {icon}
              {label}
            </div>
            <span className={`h-4 w-4 rounded-full ${getColor(statusMap[key])}`} />
          </div>
          <p className="text-2xl">
            {key === 'motion'
              ? sensors[key] != null
                ? (sensors[key] ? 'Detected' : 'None')
                : 'N/A'
              : `${sensors[key] ?? 'N/A'} ${unit}`}
          </p>
        </div>
      ))}
    </div>
  );
}
