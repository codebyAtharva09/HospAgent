import React from 'react';

interface SupplyItem {
    item: string;
    available: number;
    required: number;
    status: string; // We will re-compute this for display, but keep for compatibility
}

interface Props {
    supplyPlan: SupplyItem[];
}

const SupplyCard: React.FC<Props> = ({ supplyPlan }) => {
    if (!supplyPlan || supplyPlan.length === 0) return null;

    // Helper to compute status and color
    const getStatus = (available: number, required: number) => {
        if (required === 0) return { label: 'OK', bg: '#DCFCE7', text: '#15803D' };

        const ratio = available / required;

        if (ratio >= 1.0) return { label: 'OK', bg: '#DCFCE7', text: '#15803D' };
        if (ratio >= 0.7) return { label: 'MEDIUM', bg: '#FEF9C3', text: '#A16207' };
        if (ratio >= 0.4) return { label: 'LOW', bg: '#FED7AA', text: '#C2410C' };
        return { label: 'CRITICAL', bg: '#FEE2E2', text: '#991B1B' };
    };

    return (
        <div className="card">
            <h3 className="card-title">Critical Supplies</h3>

            <div className="overflow-x-auto">
                <table className="w-full text-sm text-left border-collapse">
                    <thead className="text-xs text-slate-500 uppercase bg-slate-50">
                        <tr>
                            <th className="px-3 py-2">Item</th>
                            <th className="px-3 py-2 text-center">Qty (Avail / Req)</th>
                            <th className="px-3 py-2 text-right">Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {supplyPlan.map((supply, idx) => {
                            // Use backend values if available, otherwise fallback (though backend should provide)
                            const available = supply.available !== undefined ? supply.available : 0;
                            const required = supply.required !== undefined ? supply.required : 0;

                            const status = getStatus(available, required);

                            return (
                                <tr key={idx} className="border-b border-slate-100 last:border-0">
                                    <td className="px-3 py-3 font-medium text-slate-700">{supply.item}</td>
                                    <td className="px-3 py-3 text-center text-slate-600">
                                        <span className="font-semibold">{available}</span>
                                        <span className="text-slate-400 mx-1">/</span>
                                        <span>{required}</span>
                                    </td>
                                    <td className="px-3 py-3 text-right">
                                        <span
                                            className="px-2 py-1 rounded-full text-[10px] font-bold"
                                            style={{ backgroundColor: status.bg, color: status.text }}
                                        >
                                            {status.label}
                                        </span>
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>

            {supplyPlan.length === 0 && (
                <p className="text-center text-slate-400 text-sm py-4">No critical supplies configured.</p>
            )}
        </div>
    );
};

export default SupplyCard;
