import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function ProtectedRoute() {
  const { token, loading } = useAuth();

  if (loading) {
    return <div className="p-6 text-center">Loading...</div>; // or spinner
  }

  return token ? <Outlet /> : <Navigate to="/login" />;
}
