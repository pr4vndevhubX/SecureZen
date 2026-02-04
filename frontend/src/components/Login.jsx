import React, { useState } from 'react';
import { Mail, Lock, User, AlertCircle, Shield, CheckCircle2 } from 'lucide-react';
import { API_BASE_URL } from '../config';

const Login = ({ onLoginSuccess }) => {
    const [isRegister, setIsRegister] = useState(false);
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        fullName: ''
    });
    const [error, setError] = useState('');
    const [successMessage, setSuccessMessage] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccessMessage('');
        setLoading(true);

        try {
            const endpoint = isRegister ? '/api/auth/register' : '/api/auth/login';
            const payload = isRegister
                ? { email: formData.email, password: formData.password, full_name: formData.fullName }
                : { email: formData.email, password: formData.password };

            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Authentication failed');
            }

            if (isRegister) {
                // If registration successful, show success message and switch to login
                setSuccessMessage('Successfully registered! Please log in with your credentials.');
                setIsRegister(false);
                setFormData({ email: formData.email, password: '', fullName: '' }); // Keep email for convenience
            } else {
                // For login, proceed as before
                localStorage.setItem('auth_token', data.access_token);
                localStorage.setItem('user', JSON.stringify(data.user));
                onLoginSuccess(data.user);
            }

        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-[#0a0e27] via-[#1a1f3a] to-[#0a0e27] flex items-center justify-center p-4">
            <div className="w-full max-w-md">
                {/* Logo/Header */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-16 h-16 bg-[#00d4ff]/10 rounded-2xl mb-4">
                        <Shield className="w-8 h-8 text-[#00d4ff]" />
                    </div>
                    <h1 className="text-3xl font-bold text-white mb-2">SecureZen</h1>
                    <p className="text-gray-400">Intelligent Security Operations Center</p>
                </div>

                {/* Login/Register Card */}
                <div className="bg-[#1a1f3a] border border-[#2a2f4a] rounded-2xl p-8 shadow-2xl">
                    {/* Tab Switcher */}
                    <div className="flex gap-2 mb-6 bg-[#0a0e27] p-1 rounded-lg">
                        <button
                            onClick={() => {
                                setIsRegister(false);
                                setError('');
                                setSuccessMessage('');
                            }}
                            type="button"
                            className={`flex-1 py-2 px-4 rounded-md font-medium transition-all ${!isRegister
                                ? 'bg-[#00d4ff] text-white'
                                : 'text-gray-400 hover:text-white'
                                }`}
                        >
                            Login
                        </button>
                        <button
                            onClick={() => {
                                setIsRegister(true);
                                setError('');
                                setSuccessMessage('');
                            }}
                            type="button"
                            className={`flex-1 py-2 px-4 rounded-md font-medium transition-all ${isRegister
                                ? 'bg-[#00d4ff] text-white'
                                : 'text-gray-400 hover:text-white'
                                }`}
                        >
                            Register
                        </button>
                    </div>

                    {/* Success Message */}
                    {successMessage && (
                        <div className="mb-4 p-3 bg-green-500/10 border border-green-500/50 rounded-lg flex items-center gap-2 animate-in fade-in zoom-in duration-300">
                            <CheckCircle2 className="w-5 h-5 text-green-500" />
                            <span className="text-green-400 text-xs font-bold uppercase tracking-tighter leading-tight">{successMessage}</span>
                        </div>
                    )}

                    {/* Error Message */}
                    {error && (
                        <div className="mb-4 p-3 bg-red-500/10 border border-red-500/50 rounded-lg flex items-center gap-2 animate-in fade-in zoom-in duration-300">
                            <AlertCircle className="w-5 h-5 text-red-500" />
                            <span className="text-red-400 text-xs font-bold uppercase tracking-tighter leading-tight">{error}</span>
                        </div>
                    )}

                    {/* Form */}
                    <form onSubmit={handleSubmit} className="space-y-4">
                        {/* Full Name (Register only) */}
                        {isRegister && (
                            <div>
                                <label className="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">
                                    Full Name
                                </label>
                                <div className="relative">
                                    <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                                    <input
                                        type="text"
                                        name="fullName"
                                        value={formData.fullName}
                                        onChange={handleChange}
                                        required={isRegister}
                                        className="w-full bg-[#0a0e27] border border-[#2a2f4a] rounded-lg pl-10 pr-4 py-3 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-[#00d4ff] transition-colors"
                                        placeholder="ALAN TURING"
                                    />
                                </div>
                            </div>
                        )}

                        {/* Email */}
                        <div>
                            <label className="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">
                                Email Core
                            </label>
                            <div className="relative">
                                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                                <input
                                    type="email"
                                    name="email"
                                    value={formData.email}
                                    onChange={handleChange}
                                    required
                                    className="w-full bg-[#0a0e27] border border-[#2a2f4a] rounded-lg pl-10 pr-4 py-3 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-[#00d4ff] transition-colors"
                                    placeholder="operator@krya.ai"
                                />
                            </div>
                        </div>

                        {/* Password */}
                        <div>
                            <label className="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">
                                Access Code
                            </label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                                <input
                                    type="password"
                                    name="password"
                                    value={formData.password}
                                    onChange={handleChange}
                                    required
                                    minLength={6}
                                    className="w-full bg-[#0a0e27] border border-[#2a2f4a] rounded-lg pl-10 pr-4 py-3 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-[#00d4ff] transition-colors"
                                    placeholder="••••••••"
                                />
                            </div>
                        </div>

                        {/* Forgot Password (Login only) */}
                        {!isRegister && (
                            <div className="text-right">
                                <button
                                    type="button"
                                    className="text-[10px] font-bold uppercase text-[#00d4ff] hover:text-white transition-colors tracking-widest"
                                >
                                    Recovery Neural Link?
                                </button>
                            </div>
                        )}

                        {/* Submit Button */}
                        <button
                            type="submit"
                            disabled={loading}
                            className="group w-full bg-[#00d4ff] hover:bg-white text-[#0a0e27] font-bold py-4 rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed uppercase tracking-[0.2em] text-xs shadow-[0_0_20px_rgba(0,212,255,0.3)] active:scale-95 flex items-center justify-center gap-3 overflow-hidden relative"
                        >
                            <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300" />
                            <span className="relative z-10 flex items-center gap-2">
                                {loading ? (
                                    <>
                                        <div className="w-4 h-4 border-2 border-[#0a0e27] border-t-transparent rounded-full animate-spin" />
                                        <span>Initializing...</span>
                                    </>
                                ) : (
                                    <>
                                        {isRegister ? 'Authorize Account' : 'Establish Link'}
                                    </>
                                )}
                            </span>
                        </button>
                    </form>
                </div>

                {/* Footer */}
                <p className="text-center text-gray-500 text-[10px] font-bold uppercase tracking-[0.5em] mt-8 opacity-50">
                    Neural SOC Interface • V2.4.0
                </p>
            </div>
        </div>
    );
};

export default Login;
