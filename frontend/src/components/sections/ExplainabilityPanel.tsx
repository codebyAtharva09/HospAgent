import React from 'react';
import { motion } from 'framer-motion';
import { AlertCircle, Thermometer, Wind, Activity, Users, Calendar } from 'lucide-react';

interface Props {
    explanations: string[];
}

const ExplainabilityPanel: React.FC<Props> = ({ explanations }) => {
    if (!explanations || explanations.length === 0) return null;

    const getIcon = (text: string) => {
        if (text.includes('AQI') || text.includes('PM2.5')) return <Wind className="w-5 h-5 text-blue-500" />;
        if (text.includes('Temperature') || text.includes('Heat')) return <Thermometer className="w-5 h-5 text-orange-500" />;
        if (text.includes('Epidemic')) return <Activity className="w-5 h-5 text-red-500" />;
        if (text.includes('ICU')) return <Users className="w-5 h-5 text-purple-500" />;
        if (text.includes('Festival')) return <Calendar className="w-5 h-5 text-yellow-500" />;
        return <AlertCircle className="w-5 h-5 text-slate-500" />;
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white/80 backdrop-blur-lg rounded-3xl border border-slate-200 shadow-lg shadow-blue-500/10 p-6 h-full"
        >
            <div className="flex items-center gap-2 mb-6">
                <div className="p-2 bg-blue-50 rounded-xl">
                    <Activity className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                    <h3 className="text-lg font-bold text-slate-900">AI Risk Analysis</h3>
                    <p className="text-xs text-slate-500">Why is risk high today?</p>
                </div>
            </div>

            <div className="space-y-4">
                {explanations.map((text, idx) => (
                    <motion.div
                        key={idx}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: idx * 0.1 }}
                        className="flex items-start gap-3 p-3 rounded-2xl bg-slate-50 border border-slate-100 hover:bg-white hover:shadow-md transition-all duration-300"
                    >
                        <div className="mt-0.5">
                            {getIcon(text)}
                        </div>
                        <p className="text-sm font-medium text-slate-700 leading-relaxed">
                            {text}
                        </p>
                    </motion.div>
                ))}
            </div>

            <div className="mt-6 pt-4 border-t border-slate-100">
                <div className="flex items-center gap-2 text-xs text-slate-400">
                    <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                    AI Model Confidence: 94%
                </div>
            </div>
        </motion.div>
    );
};

export default ExplainabilityPanel;
