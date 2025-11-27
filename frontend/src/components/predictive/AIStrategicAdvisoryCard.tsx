import React from 'react';
import { Activity, BrainCircuit } from 'lucide-react';

interface AIStrategicAdvisoryProps {
    riskIndex: number;
    riskLevel: string;
    factors: string[];
    confidence?: number;
}

const AIStrategicAdvisoryCard: React.FC<AIStrategicAdvisoryProps> = ({ riskIndex, riskLevel, factors, confidence }) => {
    // Combine factors into a single advisory string or use a default
    const advisoryText = factors.length > 0
        ? factors.join(". ") + "."
        : "System operating normally. No critical alerts detected.";

    return (
        <div className="bg-blue-900/10 border border-blue-500/30 rounded-2xl p-6 flex flex-col gap-4">
            <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-500/20 rounded-lg">
                    <BrainCircuit className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                    <h3 className="text-blue-700 font-bold text-sm uppercase tracking-wider">AI Strategic Advisory</h3>
                    {confidence && (
                        <p className="text-xs text-blue-500">Model Confidence: {(confidence * 100).toFixed(0)}%</p>
                    )}
                </div>
            </div>

            <div className="bg-white/50 rounded-xl p-4 border border-blue-100">
                <p className="text-lg font-medium leading-relaxed text-slate-700">
                    "{advisoryText}"
                </p>
            </div>
        </div>
    );
};

export default AIStrategicAdvisoryCard;
