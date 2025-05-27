import React, { useState } from 'react';
import api from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { FaEye, FaEyeSlash } from 'react-icons/fa';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

export default function ChangePassword() {
  const [newPassword, setNewPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [errors, setErrors] = useState([]);
  const [showPassword, setShowPassword] = useState(false);
  const { token } = useAuth();
  const navigate = useNavigate();

  const validatePassword = (pw) => {
    const errs = [];
    if (pw.length < 8) errs.push('Minimum 8 characters');
    if (!/[A-Z]/.test(pw)) errs.push('At least 1 uppercase letter');
    if (!/\d/.test(pw)) errs.push('At least 1 digit');
    if (!/[^A-Za-z0-9]/.test(pw)) errs.push('At least 1 special character');
    return errs;
  };

  const suggestStrongPassword = () => {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+';
    let password = '';
    while (validatePassword(password).length > 0) {
      password = Array.from({ length: 12 }, () =>
        chars[Math.floor(Math.random() * chars.length)]
      ).join('');
    }
    setNewPassword(password);
    setConfirm(password);
    setErrors([]);
  };

  const handleChange = async (e) => {
    e.preventDefault();

    const validationErrors = validatePassword(newPassword);
    if (validationErrors.length > 0) {
      setErrors(validationErrors);
      return;
    }

    if (newPassword !== confirm) {
      setErrors(['Passwords do not match']);
      return;
    }

    try {
      await api.post(
        '/auth/change-password',
        { new_password: newPassword, confirm_password: confirm },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      toast.success('Password changed successfully!');
      setTimeout(() => navigate('/settings'), 1500); // 👈 Redirect to settings
    } catch (err) {
      console.error(err);
      toast.error('Failed to change password');
    }
  };

  return (
    <div className="min-h-screen flex justify-center items-center bg-gray-50">
      <form onSubmit={handleChange} className="bg-white p-8 rounded shadow max-w-sm w-full">
        <h2 className="text-2xl font-bold mb-4 text-center">Set New Password</h2>

        <div className="relative mb-2">
          <input
            type={showPassword ? 'text' : 'password'}
            placeholder="New password"
            value={newPassword}
            onChange={e => {
              setNewPassword(e.target.value);
              setErrors(validatePassword(e.target.value));
            }}
            className="block w-full border rounded px-3 py-2 pr-10"
            required
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-3 text-gray-600 hover:text-black"
          >
            {showPassword ? <FaEyeSlash /> : <FaEye />}
          </button>
        </div>

        <div className="relative mb-2">
          <input
            type={showPassword ? 'text' : 'password'}
            placeholder="Confirm password"
            value={confirm}
            onChange={e => setConfirm(e.target.value)}
            className="block w-full border rounded px-3 py-2 pr-10"
            required
          />
        </div>

        <button
          type="button"
          onClick={suggestStrongPassword}
          className="text-blue-600 mb-2 text-sm underline"
        >
          Suggest Strong Password
        </button>

        {errors.length > 0 && (
          <ul className="mb-4 text-sm text-red-600">
            {errors.map((err, idx) => (
              <li key={idx}>• {err}</li>
            ))}
          </ul>
        )}

        <button type="submit" className="w-full bg-green-600 text-white py-2 rounded">
          Save Password
        </button>

        <p className="text-xs text-gray-600 mt-2">
          Password must have at least 8 characters, 1 uppercase letter, 1 digit, and 1 special character.
        </p>

        <ToastContainer position="top-right" autoClose={2500} hideProgressBar />
      </form>
    </div>
  );
}
