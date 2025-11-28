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
        <div className="flex flex-col items-center w-full">
            <div className={`env-header flex items-center justify-center w-full mb-1 transition-opacity duration-300 ${animate ? 'opacity-50' : 'opacity-100'}`}>
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

            {/* Last Updated Indicator */}
            <div className="flex items-center gap-2 mt-1">
                <span className={`relative flex h-2 w-2`}>
                    <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${isStale ? 'bg-amber-400' : 'bg-green-400'} opacity-75`}></span>
                    <span className={`relative inline-flex rounded-full h-2 w-2 ${isStale ? 'bg-amber-500' : 'bg-green-500'}`}></span>
                </span>
                <span className="text-xs text-slate-400 font-medium">{timeLabel}</span>
            </div>
        </div>
    );
};

export default LiveEnvHeader;
