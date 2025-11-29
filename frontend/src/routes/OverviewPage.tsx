import React, { useEffect, useState } from 'react';
import { getHospitalOverview, HospitalOverviewResponse } from '../api/hospitalOverview';
import { hospitalOps, PatientSummary, Supply } from '../api/hospitalOps';
import { useAuth } from '../context/AuthContext';
import { Users, Bed, Activity, Stethoscope, Building2, HeartPulse, Truck, Package, AlertTriangle, CheckCircle, Clock, Check } from 'lucide-react';

export const OverviewPage = () => {
    const { user } = useAuth();
    const [overview, setOverview] = useState<HospitalOverviewResponse | null>(null);
    const [patientSummary, setPatientSummary] = useState<PatientSummary | null>(null);
    const [supplies, setSupplies] = useState<Supply[]>([]);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const isAdmin = user?.role === 'SUPER_ADMIN' || user?.role === 'ADMIN';

    const loadData = async () => {
        try {
            setLoading(true);
            const promises: Promise<any>[] = [
                getHospitalOverview(),
                hospitalOps.getPatientSummary(),
                hospitalOps.getSupplies()
            ];

            const results = await Promise.all(promises);
            setOverview(results[0]);
            setPatientSummary(results[1]);
            setSupplies(results[2]);

        } catch (e: any) {
            console.error("Overview load error:", e);
            setError(e.message || "Failed to load overview data");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadData();
    }, [user]);

    if (loading) return <div className="flex items-center justify-center h-full text-[#769DD7]">Loading hospital data...</div>;
    if (error) return (
        <div className="flex flex-col items-center justify-center h-full text-red-500">
            <p>Error: {error}</p>
            <button onClick={() => window.location.reload()} className="mt-4 px-4 py-2 bg-slate-100 rounded hover:bg-slate-200">Retry</button>
        </div>
    );
    if (!overview) return null;

    // Calculate Supply Status Summary
    const criticalSupplies = supplies.filter(s => s.status === 'CRITICAL');
    const lowSupplies = supplies.filter(s => s.status === 'LOW');
    const supplyStatus = criticalSupplies.length > 0 ? 'CRITICAL' : lowSupplies.length > 0 ? 'LOW' : 'OK';

    return (
        <div className="space-y-6">
            {/* Admin Banner */}
            {isAdmin && (
                <div className="bg-blue-50 border border-blue-100 p-4 rounded-xl flex items-start gap-3">
                    <Activity className="w-5 h-5 text-blue-600 mt-0.5" />
                    <div className="text-sm text-blue-800">
                        <span className="font-bold">Admin Notice:</span> The Super Admin dashboard oversees surge readiness and overall hospital status.
                        Pharmacy inventory is managed by the Pharmacist, and patient admission is handled by the Receptionist.
                    </div>
                </div>
            )}

            {/* Header */}
            <div className="flex justify-between items-end">
                <div>
                    <h2 className="text-2xl font-bold text-slate-800">Hospital Overview</h2>
                    <p className="text-slate-500">Real-time capacity and inventory snapshot.</p>
                </div>
                {patientSummary && (
                    <div className="flex gap-4 text-sm">
                        <div className="px-4 py-2 bg-white rounded-lg border border-slate-200 shadow-sm">
                            <span className="text-slate-500">Active Inpatients:</span> <span className="font-bold text-slate-800">{patientSummary.active_inpatients}</span>
                        </div>
                        <div className="px-4 py-2 bg-white rounded-lg border border-slate-200 shadow-sm">
                            <span className="text-slate-500">Discharged Today:</span> <span className="font-bold text-slate-800">{patientSummary.discharged_today}</span>
                        </div>
                    </div>
                )}
            </div>
            {/* Row 1: Key Capacity Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard icon={<Users className="text-blue-500" />} label="Total Doctors" value={overview.total_doctors} sub="Registered Staff" />
                <StatCard icon={<Users className="text-purple-500" />} label="Total Nurses" value={overview.total_nurses} sub="Registered Staff" />
                <StatCard icon={<Bed className="text-emerald-500" />} label="Bed Occupancy" value={`${overview.current_inpatients || 0} / ${overview.total_beds}`} sub={`${overview.icus_occupied || 0} / ${overview.icu_beds} ICU Beds`} />
                <StatCard
                    icon={<Package className={supplyStatus === 'CRITICAL' ? "text-red-500" : supplyStatus === 'LOW' ? "text-amber-500" : "text-emerald-500"} />}
                    label="Pharmacy & Inventory"
                    value={supplyStatus}
                    sub={`${criticalSupplies.length} Critical, ${lowSupplies.length} Low`}
                />
            </div>

            {/* Row 2: Detailed Breakdown */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

                {/* Left Column: Specializations & Infrastructure */}
                <div className="space-y-6">
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
                            <InfraItem label="ICU Beds" value={`${overview.icus_occupied || 0} / ${overview.icu_beds}`} icon={<HeartPulse className="w-4 h-4 text-red-400" />} />
                            <InfraItem label="Ventilators" value={overview.ventilators} icon={<WindIcon className="w-4 h-4 text-blue-400" />} />
                            <InfraItem label="Ambulances" value={overview.ambulances} icon={<Truck className="w-4 h-4 text-orange-400" />} />
                            <InfraItem label="Total Beds" value={`${overview.current_inpatients || 0} / ${overview.total_beds}`} icon={<Bed className="w-4 h-4 text-emerald-400" />} />
                        </div>
                    </div>
                </div>

                {/* Right Column: Patient Stats */}
                <div className="space-y-6">
                    {/* Patient Department Breakdown */}
                    {patientSummary && (
                        <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm">
                            <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
                                <Activity className="w-5 h-5 text-[#769DD7]" />
                                Active Patients by Dept
                            </h3>
                            <div className="space-y-3">
                                {patientSummary.by_department.map((dept, idx) => (
                                    <div key={idx} className="flex items-center justify-between">
                                        <span className="text-sm text-slate-600 font-medium">{dept.department}</span>
                                        <div className="flex items-center gap-3 flex-1 justify-end">
                                            <div className="w-24 h-2 bg-slate-100 rounded-full overflow-hidden">
                                                <div
                                                    className="h-full bg-blue-500 rounded-full"
                                                    style={{ width: `${Math.min(100, (dept.count / patientSummary.active_inpatients) * 100)}%` }}
                                                />
                                            </div>
                                            <span className="text-sm font-bold text-slate-800 w-6 text-right">{dept.count}</span>
                                        </div>
                                    </div>
                                ))}
                                {patientSummary.by_department.length === 0 && (
                                    <div className="text-center text-slate-400 text-sm py-4">No active patients.</div>
                                )}
                            </div>
                        </div>
                    )}
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
