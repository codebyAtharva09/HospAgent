import React from 'react';

interface RiskData {
    timestamp: string;
    hospital_risk_index: number;
    level: string;
    breakdown: {
        aqi_risk: number;
        icu_risk: number;
    };
    contributing_factors: string[];
}

interface Props {
    riskData: RiskData | null;
}

const RiskCard: React.FC<Props> = ({ riskData }) => {
    if (!riskData) {
        return (
            <div className="card">
                <h3 className="card-title">Live Risk Index</h3>
                <p className="empty-state">Waiting for risk data...</p>
            </div>
        );
    }

    const getColor = (level: string) => {
        switch (level) {
            case 'CRITICAL': return '#DC2626';
            case 'HIGH': return '#F59E0B';
            case 'MODERATE': return '#EAB308';
            default: return '#10B981';
        }
    };

    const getBgColor = (level: string) => {
        switch (level) {
            case 'CRITICAL': return '#FEE2E2';
            case 'HIGH': return '#FED7AA';
            case 'MODERATE': return '#FEF3C7';
            default: return '#D1FAE5';
        }
    };

    return (
        <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                <div>
                    <h3 className="card-title">Live Risk Index</h3>
                    <p style={{ fontSize: '0.75rem', color: '#6B7280', marginTop: '0.25rem' }}>
                        Updated: {new Date(riskData.timestamp).toLocaleTimeString()}
                    </p>
                </div>
                <span style={{
                    padding: '0.25rem 0.75rem',
                    borderRadius: '12px',
                    fontSize: '0.75rem',
                    fontWeight: 700,
                    color: getColor(riskData.level),
                    backgroundColor: getBgColor(riskData.level),
                    border: `1px solid ${getColor(riskData.level)}40`
                }}>
                    {riskData.level}
                </span>
            </div>

            <div style={{ display: 'flex', alignItems: 'flex-end', marginBottom: '1.5rem' }}>
                <span style={{ fontSize: '3rem', fontWeight: 700, color: '#111827' }}>
                    {riskData.hospital_risk_index}
                </span>
                <span style={{ fontSize: '0.875rem', color: '#9CA3AF', marginBottom: '0.5rem', marginLeft: '0.5rem' }}>
                    / 100
                </span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem', marginBottom: '0.5rem' }}>
                        <span style={{ color: '#6B7280' }}>AQI Impact</span>
                        <span style={{ fontWeight: 600 }}>{riskData.breakdown.aqi_risk}%</span>
                    </div>
                    <div style={{ width: '100%', backgroundColor: '#E5E7EB', borderRadius: '4px', height: '6px' }}>
                        <div style={{
                            backgroundColor: '#769DD7',
                            height: '6px',
                            borderRadius: '4px',
                            width: `${riskData.breakdown.aqi_risk}%`
                        }}></div>
                    </div>
                </div>

                <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem', marginBottom: '0.5rem' }}>
                        <span style={{ color: '#6B7280' }}>ICU Pressure</span>
                        <span style={{ fontWeight: 600 }}>{riskData.breakdown.icu_risk}%</span>
                    </div>
                    <div style={{ width: '100%', backgroundColor: '#E5E7EB', borderRadius: '4px', height: '6px' }}>
                        <div style={{
                            backgroundColor: '#8B5CF6',
                            height: '6px',
                            borderRadius: '4px',
                            width: `${riskData.breakdown.icu_risk}%`
                        }}></div>
                    </div>
                </div>
            </div>

            <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid #E5E7EB' }}>
                <p style={{ fontSize: '0.75rem', fontWeight: 700, color: '#6B7280', marginBottom: '0.5rem', letterSpacing: '0.5px' }}>
                    CONTRIBUTING FACTORS
                </p>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                    {riskData.contributing_factors.map((factor, idx) => (
                        <span key={idx} style={{
                            padding: '0.25rem 0.5rem',
                            backgroundColor: '#F3F4F6',
                            color: '#4B5563',
                            fontSize: '0.625rem',
                            borderRadius: '4px'
                        }}>
                            {factor}
                        </span>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default RiskCard;
