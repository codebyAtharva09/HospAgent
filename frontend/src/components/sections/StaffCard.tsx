import React from 'react';

const StaffCard = ({ staffingPlan }) => {
    if (!staffingPlan || staffingPlan.length === 0) return null;

    // Backend returns a list where the first item is the summary for "Hospital Wide"
    const hospitalWide = staffingPlan.find(p => p.department === "Hospital Wide") || staffingPlan[0] || {};

    const { doctors, nurses, available_doctors, available_nurses } = hospitalWide;

    // Calculate shortages
    const docShortage = Math.max(0, (doctors || 0) - (available_doctors || 0));
    const nurseShortage = Math.max(0, (nurses || 0) - (available_nurses || 0));

    // Calculate percentages for bars (capped at 100%)
    const docPercent = doctors ? Math.min(100, ((available_doctors || 0) / doctors) * 100) : 0;
    const nursePercent = nurses ? Math.min(100, ((available_nurses || 0) / nurses) * 100) : 0;

    return (
        <div className="card">
            <h3 className="card-title">Staffing Recommendations</h3>

            <div className="space-y-4">
                {/* Doctors Section */}
                <div className="p-3 bg-blue-50 rounded-lg border border-blue-100">
                    <div className="flex justify-between items-center mb-2">
                        <div className="flex items-center gap-2">
                            <span className="text-xl">👨‍⚕️</span>
                            <div>
                                <p className="text-sm font-bold text-slate-700">Doctors</p>
                                <p className="text-xs text-slate-500">
                                    Available: <span className="font-semibold text-slate-700">{available_doctors || 0}</span> / Req: {doctors || 0}
                                </p>
                            </div>
                        </div>
                        {docShortage > 0 ? (
                            <span className="text-xs font-bold text-red-600 bg-red-100 px-2 py-1 rounded-full">
                                -{docShortage} Short
                            </span>
                        ) : (
                            <span className="text-xs font-bold text-green-600 bg-green-100 px-2 py-1 rounded-full">
                                OK
                            </span>
                        )}
                    </div>
                    {/* Progress Bar */}
                    <div className="w-full bg-blue-200 rounded-full h-2">
                        <div
                            className={`h-2 rounded-full ${docShortage > 0 ? 'bg-red-500' : 'bg-blue-500'}`}
                            style={{ width: `${docPercent}%` }}
                        ></div>
                    </div>
                </div>

                {/* Nurses Section */}
                <div className="p-3 bg-blue-50 rounded-lg border border-blue-100">
                    <div className="flex justify-between items-center mb-2">
                        <div className="flex items-center gap-2">
                            <span className="text-xl">👩‍⚕️</span>
                            <div>
                                <p className="text-sm font-bold text-slate-700">Nurses</p>
                                <p className="text-xs text-slate-500">
                                    Available: <span className="font-semibold text-slate-700">{available_nurses || 0}</span> / Req: {nurses || 0}
                                </p>
                            </div>
                        </div>
                        {nurseShortage > 0 ? (
                            <span className="text-xs font-bold text-red-600 bg-red-100 px-2 py-1 rounded-full">
                                -{nurseShortage} Short
                            </span>
                        ) : (
                            <span className="text-xs font-bold text-green-600 bg-green-100 px-2 py-1 rounded-full">
                                OK
                            </span>
                        )}
                    </div>
                    {/* Progress Bar */}
                    <div className="w-full bg-blue-200 rounded-full h-2">
                        <div
                            className={`h-2 rounded-full ${nurseShortage > 0 ? 'bg-red-500' : 'bg-blue-500'}`}
                            style={{ width: `${nursePercent}%` }}
                        ></div>
                    </div>
                </div>
            </div>

            {hospitalWide.notes && hospitalWide.notes.length > 0 && (
                <div className="mt-4 p-3 bg-red-50 border border-red-100 rounded-lg">
                    <p className="text-xs font-bold text-red-600 mb-1">⚠️ NOTES</p>
                    {hospitalWide.notes.map((note, idx) => (
                        <p key={idx} className="text-xs text-red-500">• {note}</p>
                    ))}
                </div>
            )}
        </div>
    );
};

export default StaffCard;
