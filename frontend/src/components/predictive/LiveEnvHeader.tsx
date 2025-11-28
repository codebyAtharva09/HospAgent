import React from 'react';

export interface CommandCenterEnv {
    aqi: number;
    pm25: number;
    temp_c: number;
    weather_label: string;
    last_updated_utc?: string;
}

type LiveEnvHeaderProps = {
    env: CommandCenterEnv | null | undefined;
    isLoading?: boolean;
    error?: string | null;
};

const LiveEnvHeader: React.FC<LiveEnvHeaderProps> = ({ env, isLoading, error }) => {
    const [timeLabel, setTimeLabel] = React.useState("Live API Data");
    const [isStale, setIsStale] = React.useState(false);
    const [animate, setAnimate] = React.useState(false);

    // Animation trigger when env updates
    React.useEffect(() => {
        if (env) {
            setAnimate(true);
            const timer = setTimeout(() => setAnimate(false), 300);
            return () => clearTimeout(timer);
        }
    }, [env]);

    // Timer for "seconds ago" updates
    React.useEffect(() => {
        if (!env?.last_updated_utc) return;

        const updateTime = () => {
            const lastUpdated = new Date(env.last_updated_utc!);
            const now = new Date();
            const diffMs = now.getTime() - lastUpdated.getTime();
            const secondsAgo = Math.floor(diffMs / 1000);
            const minutesAgo = Math.floor(diffMs / 60000);

            setIsStale(minutesAgo > 20);

            if (secondsAgo < 60) {
                setTimeLabel(`Updated ${secondsAgo} sec ago • Live`);
            } else {
                setTimeLabel(`Updated ${minutesAgo} min ago • ${minutesAgo > 20 ? 'Stale' : 'Live'}`);
            }
        };

        updateTime(); // Initial call
        const interval = setInterval(updateTime, 1000);
        return () => clearInterval(interval);
    }, [env?.last_updated_utc]);

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
        <div className="flex flex-col items-end">
            <div className={`env-header flex items-center bg-slate-50/50 px-6 py-2 rounded-2xl border border-slate-100 transition-opacity duration-300 ${animate ? 'opacity-50' : 'opacity-100'}`}>
                <div className="env-pill text-center min-w-[80px]">
                    <span className="label block text-[10px] text-slate-400 font-bold uppercase tracking-wider mb-1">Temperature</span>
                    <span className="value text-xl font-bold text-slate-700">{env.temp_c?.toFixed(1)}°C</span>
                </div>
                <div className="w-px h-8 bg-slate-200 mx-4"></div>
                <div className="env-pill text-center min-w-[80px]">
                    <span className="label block text-[10px] text-slate-400 font-bold uppercase tracking-wider mb-1">Live AQI</span>
                    <span className="value text-xl font-bold text-slate-700">{env.aqi}</span>
                </div>
                <div className="w-px h-8 bg-slate-200 mx-4"></div>
                <div className="env-pill text-center min-w-[80px]">
                    <span className="label block text-[10px] text-slate-400 font-bold uppercase tracking-wider mb-1">Weather</span>
                    <span className="value text-sm font-bold text-slate-700 mt-1">{env.weather_label}</span>
                </div>
                {env.pm25 !== undefined && (
                    <>
                        <div className="w-px h-8 bg-slate-200 mx-4"></div>
                        <div className="env-pill text-center min-w-[80px]">
                            <span className="label block text-[10px] text-slate-400 font-bold uppercase tracking-wider mb-1">PM2.5</span>
                            <span className="value text-xl font-bold text-slate-700">{env.pm25?.toFixed(1)} <span className="text-xs font-normal text-slate-400">µg/m³</span></span>
                        </div>
                    </>
                )}
            </div>

            {/* Last Updated Indicator */}
            <div className="flex items-center gap-2 mt-2 mr-2">
                <span className={`relative flex h-2 w-2`}>
                    <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${isStale ? 'bg-amber-400' : 'bg-emerald-400'} opacity-75`}></span>
                    <span className={`relative inline-flex rounded-full h-2 w-2 ${isStale ? 'bg-amber-500' : 'bg-emerald-500'}`}></span>
                </span>
                <span className="text-[10px] text-slate-400 font-medium uppercase tracking-wide">{timeLabel}</span>
            </div>
        </div>
    );
};

export default LiveEnvHeader;
