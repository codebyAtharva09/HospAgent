import React from 'react';
import { Activity } from 'lucide-react';

export const TopNavbar: React.FC = () => {
    return (
        <header className="fixed top-0 left-0 right-0 h-14 bg-white border-b border-slate-200 z-50 flex items-center px-6 shadow-sm">
            <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600">
                    <Activity className="w-5 h-5" />
                </div>
                <span className="font-bold text-lg text-slate-800 tracking-tight">HospAgent SurgeOps</span>
            </div>
        </header>
    );
};
