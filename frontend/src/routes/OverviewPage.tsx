import React, { useEffect, useState } from 'react';
import { getHospitalOverview, HospitalOverviewResponse } from '../api/hospitalOverview';
import { Users, Bed, Activity, Stethoscope, Building2, HeartPulse, Truck } from 'lucide-react';

export const OverviewPage = () => {
    const [overview, setOverview] = useState<HospitalOverviewResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        async function load() {
            try {
                setLoading(true);
                const data = await getHospitalOverview();
                setOverview(data);
            } catch (e: any) {
                console.error("Overview load error:", e);
                setError(e.message || "Failed to load overview data");
            } finally {
                setLoading(false);
            }
        }
        load();
    }, []);

    if (loading) return <div className="flex items-center justify-center h-full text-[#769DD7]">Loading hospital data...</div>;
    if (error) return (
        <div className="flex flex-col items-center justify-center h-full text-red-500">
            <p>Error: {error}</p>
            <button onClick={() => window.location.reload()} className="mt-4 px-4 py-2 bg-slate-100 rounded hover:bg-slate-200">Retry</button>
        </div>
    );
    if (!overview) return null;

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h2 className="text-2xl font-bold text-slate-800">Hospital Overview</h2>
                <p className="text-slate-500">Real-time capacity and inventory snapshot.</p>
            </div>

            {/* Row 1: Key Capacity Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard icon={<Users className="text-blue-500" />} label="Total Doctors" value={overview.total_doctors} sub="Registered Staff" />
                <StatCard icon={<Users className="text-purple-500" />} label="Total Nurses" value={overview.total_nurses} sub="Registered Staff" />
                <StatCard icon={<Bed className="text-emerald-500" />} label="Total Beds" value={overview.total_beds} sub={`${overview.icu_beds} ICU Beds`} />
                <StatCard icon={<Activity className="text-rose-500" />} label="Ambulances" value={overview.ambulances} sub={`${overview.ventilators} Ventilators`} />
            </div>

            {/* Row 2: Detailed Breakdown */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

                {/* Doctor Specializations */}
                <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm">
                    <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
                        <Stethoscope className="w-5 h-5 text-[#769DD7]" />
                        Doctor Specializations
                    </h3>
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm text-left text-slate-600">
                            <thead className="text-xs text-slate-400 uppercase bg-slate-50">
                                <tr>
                                    <th className="px-4 py-2 rounded-l-lg">Specialization</th>
                                    <th className="px-4 py-2 rounded-r-lg text-right">Count</th>
                                </tr>
                            </thead>
                            <tbody>
                                {overview.doctors_by_specialization.map((spec, idx) => (
                                    <tr key={idx} className="border-b border-slate-50 last:border-0 hover:bg-slate-50 transition-colors">
                                        <td className="px-4 py-3 font-medium">{spec.name}</td>
                                        <td className="px-4 py-3 text-right font-bold text-slate-800">{spec.count}</td>
                                    </tr>
                                ))}
                                {overview.doctors_by_specialization.length === 0 && (
                                    <tr>
                                        <td colSpan={2} className="px-4 py-3 text-center text-slate-400 italic">No specialization data available</td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Infrastructure Summary */}
                <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm">
                    <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
                        <Building2 className="w-5 h-5 text-[#769DD7]" />
                        Infrastructure & Capacity
                    </h3>
                    <div className="grid grid-cols-2 gap-4">
                        <InfraItem label="General Wards" value={overview.wards} icon={<Building2 className="w-4 h-4 text-slate-400" />} />
                        <InfraItem label="Operating Theaters" value={overview.operating_theaters} icon={<Activity className="w-4 h-4 text-slate-400" />} />
                        <InfraItem label="ICU Beds" value={overview.icu_beds} icon={<HeartPulse className="w-4 h-4 text-red-400" />} />
                        <InfraItem label="Ventilators" value={overview.ventilators} icon={<WindIcon className="w-4 h-4 text-blue-400" />} />
                        <InfraItem label="Ambulances" value={overview.ambulances} icon={<Truck className="w-4 h-4 text-orange-400" />} />
                        <InfraItem label="Total Beds" value={overview.total_beds} icon={<Bed className="w-4 h-4 text-emerald-400" />} />
                    </div>
                </div>

            </div>
        </div>
    );
};

const StatCard = ({ icon, label, value, sub }: any) => (
    <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex items-center gap-4 hover:shadow-md transition-shadow">
        <div className="p-3 bg-slate-50 rounded-xl">
            {React.cloneElement(icon, { className: `w-6 h-6 ${icon.props.className}` })}
        </div>
        <div>
            <p className="text-sm font-medium text-slate-500">{label}</p>
            <p className="text-2xl font-bold text-slate-800">{value}</p>
            <p className="text-xs text-slate-400 mt-0.5">{sub}</p>
        </div>
    </div>
);

const InfraItem = ({ label, value, icon }: any) => (
    <div className="p-4 bg-slate-50 rounded-xl border border-slate-100 flex items-center justify-between">
        <div className="flex items-center gap-3">
            {icon}
            <span className="text-sm font-medium text-slate-600">{label}</span>
        </div>
        <span className="text-lg font-bold text-slate-800">{value}</span>
    </div>
);

const WindIcon = (props: any) => (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17.7 7.7a2.5 2.5 0 1 1 1.8 4.3H2" /><path d="M9.6 4.6A2 2 0 1 1 11 8H2" /><path d="M12.6 19.4A2 2 0 1 0 14 16H2" /></svg>
);
