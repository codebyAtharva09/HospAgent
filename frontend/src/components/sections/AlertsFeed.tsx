import { useEffect, useState } from 'react';
import { Card } from "@/components/ui/card";
import { Bell, AlertTriangle, Info, CheckCircle, RefreshCw } from "lucide-react";
import api from "@/services/api";

interface Alert {
    id: string;
    type: string;
    severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
    title: string;
    message: string;
    recommendation: string;
    timestamp: string;
}

export const AlertsFeed = () => {
    const [alerts, setAlerts] = useState<Alert[]>([]);
    const [loading, setLoading] = useState(true);
    const [lastUpdated, setLastUpdated] = useState<string>("");

    const fetchAlerts = async () => {
        setLoading(true);
        try {
            const response = await api.get('/alerts/trigger?mode=display');
            if (response.data && response.data.alerts) {
                setAlerts(response.data.alerts);
                setLastUpdated(new Date().toLocaleTimeString());
            }
        } catch (error) {
            console.error("Failed to fetch alerts:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchAlerts();
        const interval = setInterval(fetchAlerts, 60000); // Refresh every minute
        return () => clearInterval(interval);
    }, []);

    const getSeverityColor = (severity: string) => {
        switch (severity) {
            case 'CRITICAL': return 'bg-rose-500/10 text-rose-500 border-rose-500/20 hover:bg-rose-500/20';
            case 'HIGH': return 'bg-orange-500/10 text-orange-500 border-orange-500/20 hover:bg-orange-500/20';
            case 'MEDIUM': return 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20 hover:bg-yellow-500/20';
            default: return 'bg-blue-500/10 text-blue-500 border-blue-500/20 hover:bg-blue-500/20';
        }
    };

    const getIcon = (type: string) => {
        switch (type) {
            case 'AQI_SURGE': return <AlertTriangle className="h-5 w-5" />;
            case 'FESTIVAL_RISK': return <Info className="h-5 w-5" />;
            case 'SUPPLY_SHORTAGE': return <AlertTriangle className="h-5 w-5" />;
            default: return <Bell className="h-5 w-5" />;
        }
    };

    return (
        <Card className="p-6 backdrop-blur-md bg-white/5 border-white/10 shadow-xl h-full flex flex-col">
            <div className="flex justify-between items-center mb-6">
                <h3 className="text-lg font-semibold flex items-center gap-2">
                    <Bell className="h-5 w-5 text-purple-500" />
                    Emergency Alerts
                </h3>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <RefreshCw className={`h-3 w-3 ${loading ? 'animate-spin' : ''}`} />
                    Updated: {lastUpdated}
                </div>
            </div>

            <div className="space-y-4 overflow-y-auto max-h-[600px] pr-2 custom-scrollbar">
                {alerts.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
                        <CheckCircle className="h-12 w-12 mb-4 text-emerald-500/50" />
                        <p>No active alerts. Operations normal.</p>
                    </div>
                ) : (
                    alerts.map((alert) => (
                        <div
                            key={alert.id}
                            className={`p-4 rounded-lg border ${getSeverityColor(alert.severity)} transition-all duration-300`}
                        >
                            <div className="flex justify-between items-start mb-2">
                                <div className="flex items-center gap-2 font-semibold">
                                    {getIcon(alert.type)}
                                    {alert.title}
                                </div>
                                <span className="text-xs opacity-70 px-2 py-0.5 rounded-full bg-black/20">
                                    {new Date(alert.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                </span>
                            </div>

                            <p className="text-sm opacity-90 mb-3 leading-relaxed">
                                {alert.message}
                            </p>

                            {alert.recommendation && (
                                <div className="mt-3 p-3 bg-black/20 rounded border border-white/5 text-sm">
                                    <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider opacity-70 mb-1 text-purple-400">
                                        <span className="w-1.5 h-1.5 rounded-full bg-purple-500 animate-pulse" />
                                        AI Recommendation
                                    </div>
                                    <p className="italic opacity-90">{alert.recommendation}</p>
                                </div>
                            )}
                        </div>
                    ))
                )}
            </div>
        </Card>
    );
};
