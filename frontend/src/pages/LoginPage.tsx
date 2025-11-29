import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Lock, Mail, Loader2 } from 'lucide-react';
import { TopNavbar } from '../components/layout/TopNavbar';

const LoginPage = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { login } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();

    const from = (location.state as any)?.from?.pathname || '/dashboard';

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const formData = new URLSearchParams();
            formData.append('username', email);
            formData.append('password', password);

            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: formData,
            });

            if (!response.ok) {
                throw new Error('Invalid credentials');
            }

            const data = await response.json();
            login(data.access_token, data.user);

            // Redirect based on role
            let targetPath = '/dashboard/overview'; // Default
            if (data.user.role === 'SUPER_ADMIN') targetPath = '/dashboard/users'; // Or overview
            if (data.user.role === 'ADMIN') targetPath = '/dashboard/overview';
            if (data.user.role === 'RECEPTION') targetPath = '/dashboard/reception';
            if (data.user.role === 'PHARMACIST') targetPath = '/dashboard/pharmacy';

            navigate(targetPath, { replace: true });
        } catch (err) {
            setError('Invalid email or password');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4 pt-14">
            <TopNavbar />
            <div className="bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden">
                <div className="p-8 bg-blue-600 text-center">
                    <h1 className="text-3xl font-bold text-white mb-2">HospAgent</h1>
                    <p className="text-blue-100">Secure Command Center Access</p>
                </div>

                <div className="p-8">
                    <form onSubmit={handleSubmit} className="space-y-6">
                        {error && (
                            <div className="p-3 bg-red-50 text-red-600 text-sm rounded-lg border border-red-100">
                                {error}
                            </div>
                        )}

                        <div className="space-y-2">
                            <label className="text-sm font-medium text-slate-700">Email Address</label>
                            <div className="relative">
                                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                                <input
                                    type="email"
                                    required
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="w-full pl-10 pr-4 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
                                    placeholder="name@hospital.com"
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-medium text-slate-700">Password</label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                                <input
                                    type="password"
                                    required
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="w-full pl-10 pr-4 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
                                    placeholder="••••••••"
                                />
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-lg transition-colors flex items-center justify-center gap-2"
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="w-5 h-5 animate-spin" />
                                    Signing in...
                                </>
                            ) : (
                                'Sign In'
                            )}
                        </button>
                    </form>

                    <div className="mt-6 p-4 bg-slate-100 rounded-xl border text-sm text-slate-700">
                        <h3 className="font-semibold mb-2">Test Accounts (For Judges)</h3>

                        <ul className="space-y-1">
                            <li><strong>Super Admin:</strong> director@hospital.com</li>
                            <li><strong>Admin:</strong> ops@hospital.com</li>
                            <li><strong>Receptionist:</strong> frontdesk@hospital.com</li>
                            <li><strong>Pharmacist:</strong> pharmacy@hospital.com</li>
                        </ul>

                        <div className="mt-3">
                            <strong>Password:</strong> password123
                        </div>
                    </div>

                    <div className="mt-6 text-center text-xs text-slate-400">
                        Protected by HospAgent Security • v2.1
                    </div>
                </div>
            </div>
        </div>
    );
};

export default LoginPage;
