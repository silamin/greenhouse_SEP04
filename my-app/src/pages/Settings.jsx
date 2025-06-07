import React from 'react';
import SettingsForm from '../components/SettingsForm';

export default function Settings() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-2xl">
        <h1 className="text-3xl font-semibold mb-6 text-center">Greenhouse Settings</h1>
        <SettingsForm />
      </div>
    </div>
  );
}
