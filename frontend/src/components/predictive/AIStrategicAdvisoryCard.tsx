import React from 'react';
import { Activity, BrainCircuit } from 'lucide-react';

interface AIStrategicAdvisoryProps {
    riskIndex: number;
    riskLevel: string;
    factors: string[];
    confidence?: number;
    lastUpdated?: string;
}

const AIStrategicAdvisoryCard: React.FC<AIStrategicAdvisoryProps> = ({ riskIndex, riskLevel, factors, confidence, lastUpdated }) => {
    // Combine factors into a single advisory string or use a default
    const advisoryText = factors.length > 0
        ? factors.join(". ") + "."
        : "System operating normally. No critical alerts detected.";

    let timeAgoText = "";
    if (lastUpdated) {
        const diff = new Date().getTime() - new Date(lastUpdated).getTime();
        const mins = Math.floor(diff / 60000);
        timeAgoText = `Risk based on env data updated ${mins} min ago.`;
    }

    return (
        <div className="bg-blue-900/10 border border-blue-500/30 rounded-2xl p-6 flex flex-col gap-4">
            <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-500/20 rounded-lg">
                    <BrainCircuit className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                    <h3 className="text-blue-700 font-bold text-sm uppercase tracking-wider">AI Strategic Advisory</h3>
                    <div className="flex flex-col">
                        {confidence && (
                            <p className="text-xs text-blue-500">Model Confidence: {(confidence * 100).toFixed(0)}%</p>
                        )}
                        {timeAgoText && (
                            <p className="text-[10px] text-blue-400 mt-0.5">{timeAgoText}</p>
                        )}
                    </div>
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
