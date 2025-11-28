import React, { useState, useEffect } from 'react';
import ErrorBoundary from '../components/ErrorBoundary';
import RiskCard from '../components/sections/RiskCard';
import SevenDayForecastCard from '../components/sections/SevenDayForecastCard';
import StaffCard from '../components/sections/StaffCard';
import SupplyCard from '../components/sections/SupplyCard';
import StaffWellbeingCard from '../components/sections/StaffWellbeingCard';
import ExplainabilityPanel from '../components/sections/ExplainabilityPanel';
import HospitalCommandBot from '../components/HospitalCommandBot';
import AIStrategicAdvisoryCard from '../components/predictive/AIStrategicAdvisoryCard';
import EmergencyAlertsCard from '../components/predictive/EmergencyAlertsCard';
import LiveEnvHeader, { CommandCenterEnv } from '../components/predictive/LiveEnvHeader';
import UpcomingFestivalsCard, { FestivalEvent } from '../components/predictive/UpcomingFestivalsCard';
import SeasonalDiseaseCard from '../components/predictive/SeasonalDiseaseCard';
import EpidemicStatusCard from '../components/predictive/EpidemicStatusCard';
import { getCommandCenter, getUpcomingFestivals } from '../api/commandCenter';
import { useAuth } from '../context/AuthContext';
import '../App.css';

export const PredictivePage = () => {
    const [data, setData] = useState({
        risk: null as any,
        forecast: [] as any[],
        staffing: [] as any[],
        supplies: [] as any[],
        festivals: [] as any[],
        env: null as CommandCenterEnv | null,
        seasonal: null as any,
        epidemic: null as any
    });
    const [upcomingFestivals, setUpcomingFestivals] = useState<FestivalEvent[]>([]);
    const [loading, setLoading] = useState(true);
    const [errorInfo, setErrorInfo] = useState<{ endpoint: string; status: number; message: string } | null>(null);
    const { user } = useAuth();

    const fetchData = async (silent = false) => {
        if (!silent) setLoading(true);
        setErrorInfo(null);
        try {
            const cmdData = await getCommandCenter();

            // Map API response to Component props

            // 1. Risk Data
            const riskData = {
                timestamp: new Date().toISOString(),
                hospital_risk_index: cmdData.risk.index,
                level: cmdData.risk.level,
                breakdown: {
                    aqi_risk: cmdData.risk.index > 50 ? Math.min(100, cmdData.risk.index * 0.6) : 20, // Derived if not explicit
                    icu_risk: cmdData.risk.index > 50 ? Math.min(100, cmdData.risk.index * 0.4) : 10  // Derived if not explicit
                },
                contributing_factors: cmdData.risk_analysis.factors || [],
                explanations: cmdData.risk_analysis.factors || [],
                confidence: cmdData.risk_analysis.confidence || 0.95,
                burnout_high_count: cmdData.wellbeing?.burnout_risk_level === 'HIGH' ? 1 : 0, // Map from wellbeing object
                burnout_note: cmdData.wellbeing?.note
            };

            // 2. Forecast Data
            // Backend returns 'days', not 'next_7_days'
            const forecastData = (cmdData.forecast.days || []).map(d => ({
                date: d.date,
                total_patients: d.total, // Backend returns 'total', not 'patients'
                breakdown: {
                    respiratory: d.respiratory || Math.round(d.total * 0.4)
                }
            }));

            // 3. Staffing Data
            const staffingData = [
                {
                    department: "Hospital Wide",
                    doctors: cmdData.staffing.today.required.doctors,
                    nurses: cmdData.staffing.today.required.nurses,
                    available_doctors: cmdData.staffing.today.available.doctors,
                    available_nurses: cmdData.staffing.today.available.nurses,
                    notes: []
                }
            ];

            // 4. Supplies Data
            // Map both 'name' (for Alerts) and 'item' (for SupplyCard)
            // Also map available/required for the new SupplyCard logic
            const suppliesData = (cmdData.supplies || []).map(s => ({
                name: s.name,
                item: s.name,
                status: s.status,
                required: s.required,
                available: s.available // Ensure backend provides this or we default in component
            }));

            // 5. Festivals (Single upcoming for alerts)
            const festivalData = cmdData.festival ? [{
                name: cmdData.festival.name,
                date: cmdData.festival.date,
                is_high_risk: cmdData.festival.risk_level === 'HIGH' || cmdData.festival.risk_level === 'CRITICAL',
                risk_level: cmdData.festival.risk_level,
                is_tomorrow: cmdData.festival.is_tomorrow,
                advisory: cmdData.festival.advisory
            }] : [];

            setData({
                risk: riskData,
                forecast: forecastData,
                staffing: staffingData,
                supplies: suppliesData,
                festivals: festivalData,
                env: cmdData.env,
                seasonal: cmdData.risk.seasonal,
                epidemic: cmdData.risk.epidemic
            });

        } catch (err: any) {
            console.error('❌ Error:', err);
            setErrorInfo({
                endpoint: '/api/command-center',
                status: err?.status || 500,
                message: err.message || 'Failed to load data'
            });
        } finally {
            if (!silent) setLoading(false);
        }
    };

    // Fetch full festival list separately
    useEffect(() => {
        const fetchFestivals = async () => {
            try {
                const events = await getUpcomingFestivals(60);
                const mappedEvents = events.map((e: any) => ({
                    id: e.id,
                    name: e.summary,
                    date: e.date,
                    risk_level: e.high_risk ? "HIGH" : "LOW"
                }));
                setUpcomingFestivals(mappedEvents as FestivalEvent[]);
            } catch (e) {
                console.error("Failed to fetch festivals", e);
            }
        };
        fetchFestivals();
    }, []);

    useEffect(() => {
        fetchData();
        const interval = setInterval(() => fetchData(true), 15000);
        return () => clearInterval(interval);
    }, []);

    return (
        <ErrorBoundary errorInfo={errorInfo}>
            <div className="space-y-6">
                {/* Controls Bar */}
                <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-wrap items-center justify-between gap-4">
                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2">
                            <span className="relative flex h-3 w-3">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                            </span>
                            <span className="text-sm font-semibold text-slate-700">Live System Active</span>
                        </div>
                    </div>

                    <div className="flex items-center gap-6">
                        <LiveEnvHeader
                            env={data.env}
                            isLoading={loading}
                            error={errorInfo?.message}
                        />
                    </div>
                </div>

                <main className="dashboard-grid">
                    <div className="grid-column col-main">
                        <SevenDayForecastCard data={data.forecast || []} />

                        {data.risk && (user?.role === 'SUPER_ADMIN' || user?.role === 'ADMIN') && (
                            <AIStrategicAdvisoryCard
                                riskIndex={data.risk.hospital_risk_index}
                                riskLevel={data.risk.level}
                                factors={data.risk.contributing_factors}
                                confidence={data.risk.confidence}
                                lastUpdated={data.env?.last_updated_utc}
                            />
                        )}
                        <RiskCard riskData={data.risk} />
                    </div>
                    <div className="grid-column col-secondary">
                        <StaffCard staffingPlan={data.staffing || []} />
                        <SupplyCard supplyPlan={data.supplies || []} />
                        <UpcomingFestivalsCard events={upcomingFestivals} />
                    </div>
                    <div className="grid-column col-sidebar">
                        {data.risk && (
                            <EmergencyAlertsCard
                                riskLevel={data.risk.level}
                                festival={data.festivals[0] || null}
                                supplies={data.supplies}
                            />
                        )}
                        <ExplainabilityPanel explanations={data.risk?.explanations || []} />

                        {data.seasonal && (
                            <SeasonalDiseaseCard
                                activeDiseases={data.seasonal.active_diseases}
                                riskIndex={data.seasonal.seasonal_risk_index}
                                commentary={data.seasonal.commentary}
                            />
                        )}

                        {data.epidemic && (
                            <EpidemicStatusCard
                                level={data.epidemic.level}
                                reason={data.epidemic.reason}
                                index={data.epidemic.epidemic_index}
                            />
                        )}

                        <StaffWellbeingCard riskData={data.risk} />
                    </div>
                </main>

                <HospitalCommandBot contextData={data} />
            </div>
        </ErrorBoundary >
    );
};
