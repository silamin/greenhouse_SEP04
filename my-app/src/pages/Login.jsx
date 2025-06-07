import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { FaEye, FaEyeSlash } from 'react-icons/fa';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await api.post('/auth/token', { username, password });
      const { access_token, is_first_login } = response.data;
      login(access_token);

      toast.success('Login successful!');

      setTimeout(() => {
        navigate(is_first_login ? '/change-password' : '/');
      }, 1500);
    } catch (error) {
      console.error('Login failed:', error);
      toast.error('Invalid username or password');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <form onSubmit={handleSubmit} className="bg-white p-8 rounded shadow-md w-full max-w-sm">
        <h2 className="text-2xl font-bold mb-4 text-center">Login</h2>

        <label className="block mb-3">
          <span className="text-gray-700">Username</span>
          <input
            type="text"
            required
            value={username}
            onChange={e => setUsername(e.target.value)}
            className="mt-1 block w-full px-3 py-2 border rounded"
          />
        </label>

        <label className="block mb-4 relative">
          <span className="text-gray-700">Password</span>
          <input
            type={showPassword ? 'text' : 'password'}
            required
            value={password}
            onChange={e => setPassword(e.target.value)}
            className="mt-1 block w-full px-3 py-2 border rounded pr-10"
          />
          <span
            className="absolute right-3 top-9 text-gray-600 cursor-pointer"
            onClick={() => setShowPassword(prev => !prev)}
          >
            {showPassword ? <FaEyeSlash /> : <FaEye />}
          </span>
        </label>

        <button type="submit" className="w-full bg-blue-500 text-white py-2 rounded">
          Login
        </button>
      </form>

      {/* Toast messages */}
      <ToastContainer position="top-right" autoClose={2500} hideProgressBar />
    </div>
  );
}
