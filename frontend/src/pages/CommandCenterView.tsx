import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
    Activity, Users, Wind, AlertTriangle,
    ArrowLeft, Clock, ShieldAlert, Thermometer
} from 'lucide-react';

const API_BASE = 'http://localhost:8000';

const CommandCenterView = () => {
    const navigate = useNavigate();
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await fetch(`${API_BASE}/api/predict/live`);
                const json = await res.json();
                setData(json);
                setLoading(false);
            } catch (err) {
                console.error(err);
            }
        };
        fetchData();
        const interval = setInterval(fetchData, 30000);
        return () => clearInterval(interval);
    }, []);

    if (loading) return <div className="min-h-screen bg-slate-950 flex items-center justify-center text-blue-500">Loading Command Center...</div>;

    const riskLevel = data?.risk?.level || 'UNKNOWN';
    const riskScore = data?.risk?.hospital_risk_index || 0;
    const aqi = data?.env?.aqi_number || 0;
    const temp = data?.env?.temperature_c || 0;
    const staffing = data?.staffing?.[0] || {};
    const explanation = data?.risk?.explanations?.[0] || "System operating normally";

    const getRiskColor = (level: string) => {
        if (level === 'CRITICAL') return 'text-red-500 border-red-500 bg-red-500/10';
        if (level === 'HIGH') return 'text-orange-500 border-orange-500 bg-orange-500/10';
        return 'text-green-500 border-green-500 bg-green-500/10';
    };

    return (
        <div className="min-h-screen bg-slate-950 text-white p-6 font-mono overflow-hidden relative">
            {/* Background Grid */}
            <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] opacity-20 pointer-events-none"></div>

            {/* Header */}
            <header className="flex justify-between items-center mb-8 border-b border-slate-800 pb-4 relative z-10">
                <div className="flex items-center gap-4">
                    <button
                        onClick={() => navigate('/dashboard')}
                        className="p-2 hover:bg-slate-800 rounded-lg transition-colors text-slate-400 hover:text-white"
                    >
                        <ArrowLeft className="w-6 h-6" />
                    </button>
                    <div>
                        <h1 className="text-2xl font-bold tracking-wider text-blue-400">COMMAND CENTER</h1>
                        <p className="text-xs text-slate-500 flex items-center gap-2">
                            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                            LIVE OPERATIONS • MUMBAI GOREGAON
                        </p>
                    </div>
                </div>
                <div className="text-right">
                    <div className="text-3xl font-bold">{new Date().toLocaleTimeString()}</div>
                    <div className="text-sm text-slate-500">{new Date().toLocaleDateString()}</div>
                </div>
            </header>

            {/* Main Grid */}
            <div className="grid grid-cols-12 gap-6 relative z-10 h-[calc(100vh-140px)]">

                {/* Left Column: Risk & Environment */}
                <div className="col-span-4 flex flex-col gap-6">
                    {/* Big Risk Gauge */}
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className={`flex-1 rounded-3xl border-2 ${getRiskColor(riskLevel)} p-8 flex flex-col items-center justify-center relative overflow-hidden`}
                    >
                        <div className="absolute inset-0 bg-gradient-to-b from-transparent to-black/50"></div>
                        <ShieldAlert className="w-16 h-16 mb-4 opacity-80" />
                        <h2 className="text-xl font-bold uppercase tracking-widest mb-2 opacity-70">Hospital Risk Index</h2>
                        <div className="text-9xl font-black tracking-tighter mb-4 drop-shadow-[0_0_15px_rgba(255,255,255,0.3)]">
                            {riskScore}
                        </div>
                        <div className="text-3xl font-bold tracking-widest uppercase">{riskLevel}</div>
                    </motion.div>

                    {/* Environment Stats */}
                    <div className="h-48 grid grid-cols-2 gap-4">
                        <div className="bg-slate-900/50 rounded-2xl border border-slate-800 p-6 flex flex-col justify-between">
                            <div className="flex items-center gap-2 text-slate-400">
                                <Wind className="w-5 h-5" />
                                <span className="text-sm font-bold">LIVE AQI</span>
                            </div>
                            <div className="text-5xl font-bold text-blue-400">{aqi}</div>
                            <div className="text-xs text-slate-500">PM2.5: {data?.env?.pollutants?.pm2_5}</div>
                        </div>
                        <div className="bg-slate-900/50 rounded-2xl border border-slate-800 p-6 flex flex-col justify-between">
                            <div className="flex items-center gap-2 text-slate-400">
                                <Thermometer className="w-5 h-5" />
                                <span className="text-sm font-bold">TEMP</span>
                            </div>
                            <div className="text-5xl font-bold text-orange-400">{temp}°C</div>
                            <div className="text-xs text-slate-500 capitalize">{data?.env?.weather_desc}</div>
                        </div>
                    </div>
                </div>

                {/* Center Column: Advisory & Map/Details */}
                <div className="col-span-5 flex flex-col gap-6">
                    {/* Main Advisory */}
                    <div className="bg-blue-900/20 border border-blue-500/30 rounded-2xl p-6 flex items-start gap-4">
                        <div className="p-3 bg-blue-500/20 rounded-xl">
                            <Activity className="w-8 h-8 text-blue-400" />
                        </div>
                        <div>
                            <h3 className="text-blue-400 font-bold text-sm uppercase mb-1">AI Strategic Advisory</h3>
                            <p className="text-xl font-medium leading-relaxed text-blue-100">
                                "{explanation}"
                            </p>
                        </div>
                    </div>

                    {/* Staffing Requirement */}
                    <div className="flex-1 bg-slate-900/50 border border-slate-800 rounded-3xl p-8">
                        <h3 className="text-slate-400 font-bold uppercase tracking-wider mb-8 flex items-center gap-2">
                            <Users className="w-5 h-5" /> Next 24h Staffing Demand
                        </h3>

                        <div className="space-y-8">
                            <div>
                                <div className="flex justify-between items-end mb-2">
                                    <span className="text-2xl font-bold">Doctors</span>
                                    <span className="text-4xl font-bold text-blue-400">{staffing.doctors || 0}</span>
                                </div>
                                <div className="w-full bg-slate-800 h-4 rounded-full overflow-hidden">
                                    <motion.div
                                        initial={{ width: 0 }}
                                        animate={{ width: `${Math.min((staffing.doctors || 0) * 2, 100)}%` }}
                                        className="h-full bg-blue-500"
                                    ></motion.div>
                                </div>
                            </div>

                            <div>
                                <div className="flex justify-between items-end mb-2">
                                    <span className="text-2xl font-bold">Nurses</span>
                                    <span className="text-4xl font-bold text-purple-400">{staffing.nurses || 0}</span>
                                </div>
                                <div className="w-full bg-slate-800 h-4 rounded-full overflow-hidden">
                                    <motion.div
                                        initial={{ width: 0 }}
                                        animate={{ width: `${Math.min((staffing.nurses || 0) * 1.5, 100)}%` }}
                                        className="h-full bg-purple-500"
                                    ></motion.div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Right Column: Alerts & Supplies */}
                <div className="col-span-3 flex flex-col gap-6">
                    {/* Festival Alert */}
                    {data?.festivals?.some((f: any) => f.is_high_risk) ? (
                        <div className="bg-red-900/20 border border-red-500/50 rounded-2xl p-6 animate-pulse">
                            <div className="flex items-center gap-3 mb-2">
                                <AlertTriangle className="w-6 h-6 text-red-500" />
                                <h3 className="text-red-500 font-bold uppercase">High Risk Event</h3>
                            </div>
                            <p className="text-red-200 text-lg font-bold">
                                {data.festivals.find((f: any) => f.is_high_risk)?.name}
                            </p>
                            <p className="text-red-400 text-sm mt-1">Surge protocols recommended</p>
                        </div>
                    ) : (
                        <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 opacity-50">
                            <h3 className="text-slate-500 font-bold uppercase">No Major Events</h3>
                        </div>
                    )}

                    {/* Supply Status */}
                    <div className="flex-1 bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
                        <h3 className="text-slate-400 font-bold uppercase tracking-wider mb-6">Critical Supplies</h3>
                        <div className="space-y-4">
                            {data?.supplies?.map((s: any, i: number) => (
                                <div key={i} className="flex justify-between items-center p-3 bg-slate-800/50 rounded-xl border border-slate-700">
                                    <span className="font-medium">{s.item}</span>
                                    <span className={`px-2 py-1 rounded text-xs font-bold ${s.status === 'OK' ? 'bg-green-500/20 text-green-400' :
                                            s.status === 'LOW' ? 'bg-red-500/20 text-red-400' : 'bg-yellow-500/20 text-yellow-400'
                                        }`}>
                                        {s.status}
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

            </div>
        </div>
    );
};

export default CommandCenterView;
