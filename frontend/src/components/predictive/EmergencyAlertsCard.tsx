import React from 'react';
import { AlertTriangle, Siren } from 'lucide-react';

interface EmergencyAlertsProps {
    riskLevel: string;
    festival?: {
        name: string | null;
        date: string | null;
        risk_level: string | null;
        is_tomorrow: boolean;
        advisory: string | null;
    } | null;
    supplies: { name: string; status: string }[];
}

const EmergencyAlertsCard: React.FC<EmergencyAlertsProps> = ({ riskLevel, festival, supplies }) => {
    const alerts: string[] = [];

    // 1. Overall Risk Alert
    if (riskLevel === "HIGH" || riskLevel === "CRITICAL") {
        alerts.push(`Overall surge risk is ${riskLevel} – activate high surge protocol.`);
    }

    // 2. Festival Alert
    if (festival && festival.risk_level === "HIGH") {
        if (festival.is_tomorrow) {
            alerts.push(`High-risk festival tomorrow: ${festival.name} – expect ER surge.`);
        } else {
            alerts.push(`Ongoing high-risk festival: ${festival.name} – monitor trauma/respiratory cases.`);
        }
    }

    // 3. Supply Alert
    supplies.forEach(supply => {
        if (supply.status === "LOW" || supply.status === "CRITICAL") {
            alerts.push(`Supply low: ${supply.name} – restock urgently.`);
        }
    });

    const hasAlerts = alerts.length > 0;

    return (
        <div className={`rounded-2xl p-6 border ${hasAlerts ? 'bg-red-50 border-red-200' : 'bg-green-50 border-green-200'}`}>
            <div className="flex items-center gap-3 mb-4">
                <div className={`p-2 rounded-lg ${hasAlerts ? 'bg-red-100' : 'bg-green-100'}`}>
                    {hasAlerts ? (
                        <Siren className="w-6 h-6 text-red-600 animate-pulse" />
                    ) : (
                        <AlertTriangle className="w-6 h-6 text-green-600" />
                    )}
                </div>
                <h3 className={`font-bold text-sm uppercase tracking-wider ${hasAlerts ? 'text-red-700' : 'text-green-700'}`}>
                    {hasAlerts ? "Active Emergency Alerts" : "System Status"}
                </h3>
            </div>

            {hasAlerts ? (
                <ul className="space-y-2">
                    {alerts.map((alert, idx) => (
                        <li key={idx} className="flex items-start gap-2 text-sm font-medium text-red-800">
                            <span className="mt-1.5 w-1.5 h-1.5 bg-red-500 rounded-full flex-shrink-0" />
                            {alert}
                        </li>
                    ))}
                </ul>
            ) : (
                <p className="text-sm font-medium text-green-800">
                    No active emergency alerts. System is stable.
                </p>
            )}
        </div>
    );
};

export default EmergencyAlertsCard;
