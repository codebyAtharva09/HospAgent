import React from 'react';

export interface CommandCenterEnv {
    aqi: number;
    pm25: number;
    temp_c: number;
    weather_label: string;
}

type LiveEnvHeaderProps = {
    env: CommandCenterEnv | null | undefined;
    isLoading?: boolean;
    error?: string | null;
};

const LiveEnvHeader: React.FC<LiveEnvHeaderProps> = ({ env, isLoading, error }) => {
    if (isLoading) {
        return (
            <div className="env-header animate-pulse">
                <div className="h-8 w-64 bg-slate-100 rounded"></div>
                <span className="text-slate-400 text-sm ml-2">Loading live data...</span>
            </div>
        );
    }

    if (error) {
        return (
            <div className="env-header">
                <span className="text-red-400 text-sm">Unable to fetch live environment data</span>
            </div>
        );
    }

    if (!env) {
        return null;
    }

    return (
        <div className="env-header flex items-center justify-center w-full">
            <div className="env-pill text-center">
                <span className="label block text-xs text-slate-500 uppercase tracking-wider mb-1">Temperature</span>
                <span className="value text-xl font-bold text-slate-800">{env.temp_c?.toFixed(1)}°C</span>
            </div>
            <div className="w-px h-10 bg-slate-200 mx-6"></div>
            <div className="env-pill text-center">
                <span className="label block text-xs text-slate-500 uppercase tracking-wider mb-1">Live AQI</span>
                <span className="value text-xl font-bold text-slate-800">{env.aqi}</span>
            </div>
            <div className="w-px h-10 bg-slate-200 mx-6"></div>
            <div className="env-pill text-center">
                <span className="label block text-xs text-slate-500 uppercase tracking-wider mb-1">Weather</span>
                <span className="value text-xl font-bold text-slate-800">{env.weather_label}</span>
            </div>
            {env.pm25 !== undefined && (
                <>
                    <div className="w-px h-10 bg-slate-200 mx-6"></div>
                    <div className="env-pill text-center">
                        <span className="label block text-xs text-slate-500 uppercase tracking-wider mb-1">PM2.5</span>
                        <span className="value text-xl font-bold text-slate-800">{env.pm25?.toFixed(1)} µg/m³</span>
                    </div>
                </>
            )}
        </div>
    );
};

export default LiveEnvHeader;
