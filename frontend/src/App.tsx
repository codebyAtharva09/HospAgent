import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import ErrorBoundary from './components/ErrorBoundary';
import RiskCard from './components/sections/RiskCard';
import SevenDayForecastCard from './components/sections/SevenDayForecastCard';
import StaffCard from './components/sections/StaffCard';
import SupplyCard from './components/sections/SupplyCard';
import CalendarPanel from './components/sections/CalendarPanel';
import StaffWellbeingCard from './components/sections/StaffWellbeingCard';
import ExplainabilityPanel from './components/sections/ExplainabilityPanel';
import HospitalCommandBot from './components/HospitalCommandBot';
import CommandCenterView from './pages/CommandCenterView';
import { LayoutDashboard, MonitorPlay } from 'lucide-react';
import './App.css';

const API_BASE = 'http://localhost:8000';

function Dashboard() {
  const navigate = useNavigate();
  const [isLiveMode, setIsLiveMode] = useState(false);
  const [liveEnv, setLiveEnv] = useState<any>(null);
  const [simParams, setSimParams] = useState({
    aqi: 150,
    epidemic: 2.0,
    festival: false
  });
  const [data, setData] = useState({
    risk: null as any,
    forecast: [] as any[],
    staffing: [] as any[],
    supplies: [] as any[],
    festivals: [] as any[]
  });
  const [loading, setLoading] = useState(true);
  const [errorInfo, setErrorInfo] = useState<{ endpoint: string; status: number; message: string } | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setErrorInfo(null);
    try {
      if (isLiveMode) {
        const res = await fetch(`${API_BASE}/api/predict/live`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const liveData = await res.json();

        setData({
          risk: liveData.risk || null,
          forecast: Array.isArray(liveData.forecast) ? liveData.forecast : [],
          staffing: Array.isArray(liveData.staffing) ? liveData.staffing : [],
          supplies: Array.isArray(liveData.supplies) ? liveData.supplies : [],
          festivals: Array.isArray(liveData.festivals) ? liveData.festivals : []
        });
        setLiveEnv(liveData.env || null);
      } else {
        const query = `aqi=${simParams.aqi}&epidemic=${simParams.epidemic}&override_festival=${simParams.festival}`;
        const [riskRes, forecastRes, staffingRes, supplyRes] = await Promise.all([
          fetch(`${API_BASE}/risk/now?${query}&slope=1.2`),
          fetch(`${API_BASE}/forecast/patients?days=7&aqi=${simParams.aqi}`),
          fetch(`${API_BASE}/plan/staffing?days=3`),
          fetch(`${API_BASE}/plan/supplies?days=3`)
        ]);
        if (!riskRes.ok || !forecastRes.ok || !staffingRes.ok || !supplyRes.ok) {
          throw new Error('Simulation endpoints failed');
        }
        const [risk, forecast, staffing, supplies] = await Promise.all([
          riskRes.json(), forecastRes.json(), staffingRes.json(), supplyRes.json()
        ]);
        setData({
          risk: risk || null,
          forecast: Array.isArray(forecast) ? forecast : [],
          staffing: Array.isArray(staffing) ? staffing : [],
          supplies: Array.isArray(supplies) ? supplies : [],
          festivals: []
        });
        setLiveEnv(null);
      }
      setLoading(false);
    } catch (err: any) {
      console.error('❌ Error:', err);
      setErrorInfo({
        endpoint: isLiveMode ? '/predict/live' : '/dashboard/summary',
        status: err?.status || 500,
        message: err.message || 'Failed to load data'
      });
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 60000);
    return () => clearInterval(interval);
  }, [isLiveMode, simParams]);

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner"></div>
        <p>Loading SurgeOps...</p>
      </div>
    );
  }

  return (
    <ErrorBoundary errorInfo={errorInfo}>
      <div className="app-container">
        {errorInfo && (
          <div className="error-banner">
            <span className="error-icon">⚠️</span>
            <span className="error-text">{errorInfo.message}</span>
            <button className="error-retry" onClick={fetchData}>Retry</button>
          </div>
        )}
        <header className="app-header">
          <div className="header-left">
            <h1 className="app-title">HospAgent SurgeOps</h1>
            <p className="app-subtitle">Live surge prediction during festivals, pollution spikes &amp; epidemics</p>
          </div>
          <div className="header-right">
            <button
              onClick={() => navigate('/command-center')}
              className="flex items-center gap-2 px-4 py-2 bg-slate-900 text-white rounded-xl hover:bg-slate-800 transition-colors mr-4 font-bold text-sm border border-slate-700 shadow-lg shadow-blue-900/20"
            >
              <MonitorPlay className="w-4 h-4" />
              Command Center
            </button>

            <div className="mode-toggle-container">
              <span className="mode-label">Live Data Mode</span>
              <button onClick={() => setIsLiveMode(!isLiveMode)} className={`toggle-switch ${isLiveMode ? 'active' : ''}`}>
                <span className="toggle-slider"></span>
              </button>
            </div>
            <div className="location-chip">📍 Mumbai, India</div>
            <div className="status-indicator">
              <span className="status-dot"></span>
              <span className="status-text">LIVE SYSTEM</span>
            </div>
          </div>
        </header>

        {isLiveMode && liveEnv && (
          <div className="live-env-banner">
            <div className="env-pill">
              <span className="env-icon">🌡️</span>
              <div className="env-data">
                <span className="env-label">Temperature</span>
                <span className="env-value">
                  {liveEnv.temperature_c ? `${Number(liveEnv.temperature_c).toFixed(1)}°C` : 'N/A'}
                </span>
              </div>
            </div>
            <div className="env-divider"></div>
            <div className="env-pill">
              <span className="env-icon">🌫️</span>
              <div className="env-data">
                <span className="env-label">Live AQI</span>
                <div className="env-value">
                  {liveEnv.aqi_number || '—'}
                  {liveEnv && (
                    <span style={{ fontSize: '0.75rem', fontWeight: 'normal', color: '#6B7280', marginLeft: '6px' }}>
                      ({liveEnv.aqi_index_1_5}/5 · {liveEnv.weather_desc})
                    </span>
                  )}
                </div>
              </div>
            </div>
            <div className="env-divider"></div>
            <div className="env-pill">
              <span className="env-icon">☁️</span>
              <div className="env-data">
                <span className="env-label">Weather</span>
                <span className="env-value">{liveEnv.weather_desc || 'N/A'}</span>
              </div>
            </div>
          </div>
        )}

        <div className={`simulation-strip ${isLiveMode ? 'disabled' : ''}`}>
          <div className="strip-header">
            <div className="strip-title">
              <span className="strip-icon">🎛️</span>
              <span>Manual Simulation Controls</span>
            </div>
            {isLiveMode && <span className="disabled-label">Disabled in Live Mode</span>}
          </div>
          <div className="controls-grid">
            <div className="control-group">
              <div className="control-label">
                <span>Air Quality Index (AQI)</span>
                <span className={`control-value ${simParams.aqi > 300 ? 'critical' : ''}`}>{simParams.aqi}</span>
              </div>
              <input type="range" min="0" max="500" step="10" value={simParams.aqi}
                onChange={(e) => setSimParams({ ...simParams, aqi: parseInt(e.target.value) })}
                className="slider aqi-slider" disabled={isLiveMode} />
            </div>
            <div className="control-group">
              <div className="control-label">
                <span>Epidemic Severity</span>
                <span className="control-value">{simParams.epidemic}</span>
              </div>
              <input type="range" min="0" max="10" step="0.5" value={simParams.epidemic}
                onChange={(e) => setSimParams({ ...simParams, epidemic: parseFloat(e.target.value) })}
                className="slider epidemic-slider" disabled={isLiveMode} />
            </div>
            <div className="control-group festival-control">
              <label className="checkbox-label">
                <input type="checkbox" checked={simParams.festival}
                  onChange={(e) => setSimParams({ ...simParams, festival: e.target.checked })}
                  disabled={isLiveMode} />
                <span className="checkbox-text">Simulate Festival</span>
              </label>
            </div>
          </div>
        </div>

        <main className="dashboard-grid">
          <div className="grid-column col-main">
            <RiskCard riskData={data.risk} />
            <SevenDayForecastCard data={data.forecast || []} />
          </div>
          <div className="grid-column col-secondary">
            <ExplainabilityPanel explanations={data.risk?.explanations || []} />
            <StaffCard staffingPlan={data.staffing || []} />
            <SupplyCard supplyPlan={data.supplies || []} />
          </div>
          <div className="grid-column col-sidebar">
            <CalendarPanel festivals={data.festivals} />
            <StaffWellbeingCard riskData={data.risk} />
          </div>
        </main>

        <HospitalCommandBot contextData={data} />
      </div>
    </ErrorBoundary >
  );
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/command-center" element={<CommandCenterView />} />
      </Routes>
    </Router>
  );
}

export default App;
