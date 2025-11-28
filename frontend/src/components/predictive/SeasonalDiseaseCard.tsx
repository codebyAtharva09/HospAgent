import React from 'react';
import { motion } from 'framer-motion';
import { CloudRain, Sun, Thermometer } from 'lucide-react';

interface SeasonalDiseaseCardProps {
    activeDiseases: string[];
    riskIndex: number; // 0-1
    commentary: string;
}

const SeasonalDiseaseCard: React.FC<SeasonalDiseaseCardProps> = ({ activeDiseases, riskIndex, commentary }) => {
    const getRiskColor = (index: number) => {
        if (index > 0.75) return 'text-red-600 bg-red-100';
        if (index > 0.5) return 'text-orange-600 bg-orange-100';
        if (index > 0.25) return 'text-yellow-600 bg-yellow-100';
        return 'text-green-600 bg-green-100';
    };

    const getRiskLabel = (index: number) => {
        if (index > 0.75) return 'CRITICAL';
        if (index > 0.5) return 'HIGH';
        if (index > 0.25) return 'MODERATE';
        return 'LOW';
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm"
        >
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2">
                    <CloudRain className="w-5 h-5 text-blue-500" />
                    Seasonal Disease Watch
                </h3>
                <span className={`px-3 py-1 rounded-full text-xs font-bold ${getRiskColor(riskIndex)}`}>
                    {getRiskLabel(riskIndex)} RISK
                </span>
            </div>

            <div className="space-y-4">
                <div>
                    <p className="text-sm text-slate-500 mb-1">Active Diseases</p>
                    <div className="flex flex-wrap gap-2">
                        {activeDiseases.length > 0 ? (
                            activeDiseases.map((d, i) => (
                                <span key={i} className="px-2 py-1 bg-slate-100 text-slate-700 rounded text-xs font-medium border border-slate-200">
                                    {d}
                                </span>
                            ))
                        ) : (
                            <span className="text-sm text-slate-400">None detected</span>
                        )}
                    </div>
                </div>

                <div>
                    <p className="text-sm text-slate-500 mb-1">Commentary</p>
                    <p className="text-sm text-slate-700">{commentary}</p>
                </div>

                <div className="w-full bg-slate-100 rounded-full h-2 mt-2">
                    <div
                        className="h-2 rounded-full transition-all duration-500 bg-gradient-to-r from-green-400 to-red-500"
                        style={{ width: `${riskIndex * 100}%` }}
                    />
                </div>
            </div>
        </motion.div>
    );
};

export default SeasonalDiseaseCard;
