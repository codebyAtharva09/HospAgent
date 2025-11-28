import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { motion } from 'framer-motion';

const LoginPage: React.FC = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        try {
            const response = await fetch('http://localhost:8000/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: new URLSearchParams({ username: email, password }),
            });

            if (!response.ok) {
                throw new Error('Login failed');
            }

            const data = await response.json();
            login(data.access_token, data.user);
            navigate('/overview');
        } catch (err) {
            setError('Invalid credentials');
        }
    };

    const quickLogin = (roleEmail: string) => {
        setEmail(roleEmail);
        setPassword('password123');
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-slate-900 text-white">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-slate-800 p-8 rounded-xl shadow-2xl w-full max-w-md"
            >
                <h2 className="text-3xl font-bold mb-6 text-center bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
                    HospAgent Login
                </h2>

                {error && <div className="bg-red-500/20 text-red-300 p-3 rounded mb-4">{error}</div>}

                <form onSubmit={handleLogin} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium mb-1">Email</label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="w-full bg-slate-700 border border-slate-600 rounded p-2 focus:ring-2 focus:ring-blue-500 outline-none"
                            required
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium mb-1">Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="w-full bg-slate-700 border border-slate-600 rounded p-2 focus:ring-2 focus:ring-blue-500 outline-none"
                            required
                        />
                    </div>
                    <button
                        type="submit"
                        className="w-full bg-blue-600 hover:bg-blue-500 py-2 rounded font-semibold transition-colors"
                    >
                        Sign In
                    </button>
                </form>

                <div className="mt-8 pt-6 border-t border-slate-700">
                    <p className="text-sm text-slate-400 mb-3 text-center">Quick Login (Demo)</p>
                    <div className="grid grid-cols-2 gap-2">
                        <button onClick={() => quickLogin('director@hospital.com')} className="text-xs bg-slate-700 hover:bg-slate-600 p-2 rounded">Super Admin</button>
                        <button onClick={() => quickLogin('ops@hospital.com')} className="text-xs bg-slate-700 hover:bg-slate-600 p-2 rounded">Admin</button>
                        <button onClick={() => quickLogin('frontdesk@hospital.com')} className="text-xs bg-slate-700 hover:bg-slate-600 p-2 rounded">Reception</button>
                        <button onClick={() => quickLogin('pharmacy@hospital.com')} className="text-xs bg-slate-700 hover:bg-slate-600 p-2 rounded">Pharmacist</button>
                    </div>
                </div>
            </motion.div>
        </div>
    );
};

export default LoginPage;
