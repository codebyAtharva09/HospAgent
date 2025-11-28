import React from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, ShieldAlert } from 'lucide-react';

interface EpidemicStatusCardProps {
    level: "LOW" | "MODERATE" | "HIGH" | "CRITICAL";
    reason: string;
    index: number; // 0-10 or 0-1
}

const EpidemicStatusCard: React.FC<EpidemicStatusCardProps> = ({ level, reason, index }) => {
    const getColor = (lvl: string) => {
        switch (lvl) {
            case 'CRITICAL': return 'bg-red-500 text-white';
            case 'HIGH': return 'bg-orange-500 text-white';
            case 'MODERATE': return 'bg-yellow-500 text-white';
            default: return 'bg-green-500 text-white';
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm"
        >
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2">
                    <ShieldAlert className="w-5 h-5 text-purple-500" />
                    Epidemic Status
                </h3>
                <span className={`px-3 py-1 rounded-full text-xs font-bold ${getColor(level)}`}>
                    {level}
                </span>
            </div>

            <div className="flex items-center gap-4 mb-4">
                <div className="flex-1">
                    <p className="text-3xl font-bold text-slate-800">{index.toFixed(1)}<span className="text-sm text-slate-400 font-normal">/10</span></p>
                    <p className="text-xs text-slate-500">Epidemic Index</p>
                </div>
                <div className="p-3 bg-purple-50 rounded-full">
                    <AlertTriangle className="w-6 h-6 text-purple-500" />
                </div>
            </div>

            <p className="text-sm text-slate-600 border-t border-slate-100 pt-3">
                {reason}
            </p>
        </motion.div>
    );
};

export default EpidemicStatusCard;
