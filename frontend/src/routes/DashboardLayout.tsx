import React from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { LayoutDashboard, Activity, MonitorPlay, User, MapPin, Settings, LogOut, Users, Bell, Pill, Calendar } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

import { TopNavbar } from '../components/layout/TopNavbar';

export const DashboardLayout = () => {
    const location = useLocation();
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const isActive = (path: string) => {
        return location.pathname.startsWith(path) ? 'bg-[#769DD7] text-white' : 'text-slate-600 hover:bg-[#CDDBE5] hover:text-slate-800';
    };

    const getPageTitle = () => {
        if (location.pathname.includes('overview')) return 'Overview';
        if (location.pathname.includes('predictive')) return 'Predictive Analytics';
        if (location.pathname.includes('command-center')) return 'Command Center';
        if (location.pathname.includes('users')) return 'User Management';
        if (location.pathname.includes('notifications')) return 'Notification Settings';
        if (location.pathname.includes('pharmacy')) return 'Pharmacy';
        if (location.pathname.includes('reception')) return 'Reception';
        return 'Dashboard';
    };

    return (
        <div className="min-h-screen bg-[#F8FAFC] pt-14"> {/* Add padding-top for fixed navbar */}
            <TopNavbar />
            <div className="flex h-[calc(100vh-3.5rem)]"> {/* Adjust height: 100vh - navbar height (3.5rem/56px) */}
                {/* Sidebar */}
                <aside className="w-64 bg-white border-r border-slate-200 flex flex-col">
                    <div className="p-6 border-b border-slate-100">
                        <h1 className="text-2xl font-bold text-[#769DD7] flex items-center gap-2">
                            <Activity className="w-8 h-8" />
                            HospAgent
                        </h1>
                    </div>

                    <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
                        <Link
                            to="/dashboard/overview"
                            className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all font-medium ${isActive('/dashboard/overview')}`}
                        >
                            <LayoutDashboard className="w-5 h-5" />
                            Overview
                        </Link>
                        <Link
                            to="/dashboard/predictive"
                            className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all font-medium ${isActive('/dashboard/predictive')}`}
                        >
                            <Activity className="w-5 h-5" />
                            Predictive
                        </Link>

                        {/* Role-Based Links */}
                        {['PHARMACIST', 'ADMIN', 'SUPER_ADMIN'].includes(user?.role || '') && (
                            <Link
                                to="/dashboard/pharmacy"
                                className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all font-medium ${isActive('/dashboard/pharmacy')}`}
                            >
                                <Pill className="w-5 h-5" />
                                Pharmacy & Inventory
                            </Link>
                        )}

                        {['RECEPTION', 'ADMIN', 'SUPER_ADMIN'].includes(user?.role || '') && (
                            <Link
                                to="/dashboard/reception"
                                className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all font-medium ${isActive('/dashboard/reception')}`}
                            >
                                <Calendar className="w-5 h-5" />
                                Reception
                            </Link>
                        )}

                        {user?.role === 'SUPER_ADMIN' && (
                            <>
                                <div className="pt-4 pb-2">
                                    <p className="px-4 text-xs font-bold text-slate-400 uppercase tracking-wider">Admin</p>
                                </div>
                                <Link
                                    to="/dashboard/users"
                                    className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all font-medium ${isActive('/dashboard/users')}`}
                                >
                                    <Users className="w-5 h-5" />
                                    Users
                                </Link>
                                <Link
                                    to="/dashboard/notifications"
                                    className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all font-medium ${isActive('/dashboard/notifications')}`}
                                >
                                    <Bell className="w-5 h-5" />
                                    Notifications
                                </Link>
                            </>
                        )}
                    </nav>

                    <div className="p-4 border-t border-slate-100">
                        <div className="flex items-center gap-3 px-4 py-3">
                            <div className="w-10 h-10 rounded-full bg-[#CDDBE5] flex items-center justify-center text-[#769DD7] font-bold">
                                {user?.full_name?.charAt(0) || 'U'}
                            </div>
                            <div className="flex-1">
                                <p className="text-sm font-bold text-slate-700 truncate w-32">{user?.full_name || 'User'}</p>
                                <p className="text-xs text-slate-500">{user?.role || 'Role'}</p>
                            </div>
                            <button onClick={handleLogout} className="text-slate-400 hover:text-red-500">
                                <LogOut className="w-4 h-4" />
                            </button>
                        </div>
                    </div>
                </aside>

                {/* Main Content */}
                <div className="flex-1 flex flex-col overflow-hidden">
                    {/* Top Header */}
                    <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-8">
                        <h2 className="text-xl font-bold text-slate-800">{getPageTitle()}</h2>

                        <div className="flex items-center gap-6">
                            <div className="flex items-center gap-2 text-slate-500 bg-slate-50 px-3 py-1 rounded-full border border-slate-100">
                                <MapPin className="w-4 h-4" />
                                <span className="text-sm font-medium">Mumbai, India</span>
                            </div>

                            <div className="flex items-center gap-2">
                                <span className="relative flex h-3 w-3">
                                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                                    <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                                </span>
                                <span className="text-sm font-medium text-green-600">Live System</span>
                            </div>

                            <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center text-slate-500">
                                <User className="w-5 h-5" />
                            </div>
                        </div>
                    </header>

                    {/* Content Area */}
                    <main className="flex-1 overflow-y-auto p-8 bg-[#F8FAFC]">
                        <div className="max-w-7xl mx-auto">
                            <Outlet />
                        </div>
                    </main>
                </div>
            </div>
        </div>
    );
};
