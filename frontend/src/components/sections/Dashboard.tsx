import React, { useState, useEffect } from 'react';
import RiskCard from './RiskCard';
import ForecastCard from './ForecastCard';
import StaffCard from './StaffCard';
import SupplyCard from './SupplyCard';
import CalendarPanel from './CalendarPanel';

const Dashboard = () => {
    // Mode State
    const [isLiveMode, setIsLiveMode] = useState(false);
    const [liveEnv, setLiveEnv] = useState(null);

    // Simulation State
    const [simParams, setSimParams] = useState({
        aqi: 150,
        epidemic: 2.0,
        festival: false
    });

    const [data, setData] = useState({
        risk: null,
        forecast: null,
        staffing: null,
        supplies: null
    });

    const [loading, setLoading] = useState(true);

    const fetchData = async () => {
        try {
            if (isLiveMode) {
                // --- LIVE MODE ---
                const res = await fetch('http://localhost:8000/predict/live');
                const liveData = await res.json();

                setData({
                    risk: liveData.risk,
                    forecast: liveData.forecast,
                    staffing: liveData.staffing,
                    supplies: liveData.supplies
                });
                setLiveEnv(liveData.env);

            } else {
                // --- SIMULATION MODE ---
                const query = `aqi=${simParams.aqi}&epidemic=${simParams.epidemic}&override_festival=${simParams.festival}`;

                const [riskRes, forecastRes, staffingRes, supplyRes] = await Promise.all([
                    fetch(`http://localhost:8000/risk/now?${query}&slope=1.2`),
                    fetch(`http://localhost:8000/forecast/patients?days=7&aqi=${simParams.aqi}`),
                    fetch(`http://localhost:8000/plan/staffing?days=3`),
                    fetch(`http://localhost:8000/plan/supplies?days=3`)
                ]);

                const risk = await riskRes.json();
                const forecast = await forecastRes.json();
                const staffing = await staffingRes.json();
                const supplies = await supplyRes.json();

                setData({ risk, forecast, staffing, supplies });
                setLiveEnv(null); // Clear live env when in sim mode
            }
            setLoading(false);
        } catch (error) {
            console.error("Error fetching dashboard data:", error);
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
        // Auto-refresh every 60s
        const interval = setInterval(fetchData, 60000);
        return () => clearInterval(interval);
    }, [isLiveMode, simParams]); // Re-fetch when mode or params change

    if (loading) {
        return (
            <div className="min-h-screen bg-[#CDDBE5] flex items-center justify-center">
                <div className="text-[#769DD7] text-xl font-bold animate-pulse">Loading SurgeOps...</div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-[#CDDBE5] p-6 font-sans">
            {/* Navbar */}
            <nav className="bg-[#769DD7] rounded-xl shadow-lg p-4 mb-6 flex justify-between items-center text-white">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight">HospAgent SurgeOps</h1>
                    <p className="text-xs opacity-90">Live surge prediction during festivals, pollution spikes & epidemics</p>
                </div>
                <div className="flex items-center space-x-4">

                    {/* Live Mode Toggle */}
                    <div className="flex items-center bg-white/10 px-3 py-1.5 rounded-lg">
                        <span className="text-xs font-medium mr-3">Live Data Mode</span>
                        <button
                            onClick={() => setIsLiveMode(!isLiveMode)}
                            className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus:outline-none ${isLiveMode ? 'bg-green-400' : 'bg-slate-300'}`}
                        >
                            <span className={`inline-block h-3 w-3 transform rounded-full bg-white transition-transform ${isLiveMode ? 'translate-x-5' : 'translate-x-1'}`} />
                        </button>
                    </div>

                    <span className="bg-white/20 px-3 py-1 rounded-full text-xs font-medium backdrop-blur-sm">
                        📍 Mumbai, India
                    </span>
                </div>
            </nav>

            {/* Live Environment Pill */}
            {isLiveMode && liveEnv && (
                <div className="mb-6 flex justify-center">
                    <div className="bg-white px-6 py-2 rounded-full shadow-sm border border-green-100 flex items-center space-x-6 animate-fade-in-up">
                        <div className="flex items-center">
                            <span className="text-xl mr-2">🌡️</span>
                            <div>
                                <p className="text-[10px] text-slate-500 uppercase font-bold">Temperature</p>
                                <p className="text-sm font-bold text-slate-800">{liveEnv.temperature}°C</p>
                            </div>
                        </div>
                        <div className="h-8 w-px bg-slate-100"></div>
                        <div className="flex items-center">
                            <span className="text-xl mr-2">🌫️</span>
                            <div>
                                <p className="text-[10px] text-slate-500 uppercase font-bold">Live AQI</p>
                                <p className={`text-sm font-bold ${liveEnv.aqi > 200 ? 'text-red-600' : 'text-slate-800'}`}>
                                    {liveEnv.aqi} ({liveEnv.aqi_level}/5)
                                </p>
                            </div>
                        </div>
                        <div className="h-8 w-px bg-slate-100"></div>
                        <div className="flex items-center">
                            <span className="text-xl mr-2">☁️</span>
                            <div>
                                <p className="text-[10px] text-slate-500 uppercase font-bold">Weather</p>
                                <p className="text-sm font-bold text-slate-800 capitalize">{liveEnv.weather_desc}</p>
                            </div>
                        </div>
                        {!liveEnv.is_live && (
                            <span className="ml-4 px-2 py-0.5 bg-yellow-100 text-yellow-700 text-[10px] rounded font-bold">MOCK DATA</span>
                        )}
                    </div>
                </div>
            )}

            {/* Simulation Controls (Disabled in Live Mode) */}
            <div className={`bg-white p-4 rounded-xl shadow-sm border border-slate-100 mb-6 transition-opacity duration-300 ${isLiveMode ? 'opacity-50 pointer-events-none grayscale' : 'opacity-100'}`}>
                <h3 className="text-sm font-bold text-slate-700 mb-3 flex items-center justify-between">
                    <div className="flex items-center">
                        <span className="mr-2">🎛️</span> Manual Simulation Controls
                    </div>
                    {isLiveMode && <span className="text-xs text-orange-500 font-medium">Disabled in Live Mode</span>}
                </h3>
                <div className="flex flex-wrap gap-6 items-center">

                    {/* AQI Slider */}
                    <div className="flex-1 min-w-[200px]">
                        <div className="flex justify-between text-xs mb-1">
                            <span className="text-slate-500">Air Quality Index (AQI)</span>
                            <span className={`font-bold ${simParams.aqi > 300 ? 'text-red-600' : 'text-slate-700'}`}>
                                {simParams.aqi}
                            </span>
                        </div>
                        <input
                            type="range" min="0" max="500" step="10"
                            value={simParams.aqi}
                            onChange={(e) => setSimParams({ ...simParams, aqi: parseInt(e.target.value) })}
                            className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-[#769DD7]"
                        />
                    </div>

                    {/* Epidemic Slider */}
                    <div className="flex-1 min-w-[200px]">
                        <div className="flex justify-between text-xs mb-1">
                            <span className="text-slate-500">Epidemic Severity</span>
                            <span className="font-bold text-slate-700">{simParams.epidemic}</span>
                        </div>
                        <input
                            type="range" min="0" max="10" step="0.5"
                            value={simParams.epidemic}
                            onChange={(e) => setSimParams({ ...simParams, epidemic: parseFloat(e.target.value) })}
                            className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-purple-500"
                        />
                    </div>

                    {/* Festival Toggle */}
                    <div className="flex items-center">
                        <label className="flex items-center cursor-pointer">
                            <div className="relative">
                                <input
                                    type="checkbox"
                                    className="sr-only"
                                    checked={simParams.festival}
                                    onChange={(e) => setSimParams({ ...simParams, festival: e.target.checked })}
                                />
                                <div className={`block w-10 h-6 rounded-full transition-colors ${simParams.festival ? 'bg-orange-400' : 'bg-slate-300'}`}></div>
                                <div className={`dot absolute left-1 top-1 bg-white w-4 h-4 rounded-full transition-transform ${simParams.festival ? 'transform translate-x-4' : ''}`}></div>
                            </div>
                            <div className="ml-3 text-sm text-slate-700 font-medium">
                                Simulate Festival
                            </div>
                        </label>
                    </div>

                </div>
            </div>

            {/* Main Grid */}
            <div className="grid grid-cols-1 md:grid-cols-12 gap-6">

                {/* Column 1: Risk & Forecast (5 cols) */}
                <div className="md:col-span-5 space-y-6">
                    <RiskCard riskData={data.risk} />
                    <ForecastCard forecastData={data.forecast} />
                </div>

                {/* Column 2: Operations (4 cols) */}
                <div className="md:col-span-4 space-y-6">
                    <StaffCard staffingPlan={data.staffing} />
                    <SupplyCard supplyPlan={data.supplies} />

                    {/* Burnout Warning (Mock) */}
                    <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-100">
                        <h4 className="text-sm font-bold text-slate-700 mb-2">Staff Wellbeing Alert</h4>
                        <div className="flex items-center text-orange-600 bg-orange-50 p-2 rounded-lg text-xs">
                            <span className="mr-2">⚠️</span>
                            3 staff members at high burnout risk.
                        </div>
                    </div>
                </div>

                {/* Column 3: Calendar (3 cols) */}
                <div className="md:col-span-3">
                    <CalendarPanel />
                </div>

            </div>
        </div>
    );
};

export default Dashboard;
