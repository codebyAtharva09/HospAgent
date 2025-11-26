import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const SevenDayForecastCard = ({ data }) => {
    if (!data || data.length === 0) {
        return (
            <div className="card">
                <h3 className="card-title">7-Day Patient Forecast</h3>
                <div className="empty-state">
                    <p>No forecast data available</p>
                </div>
            </div>
        );
    }

    // Transform data for chart
    const chartData = data.map(day => ({
        date: new Date(day.date).toLocaleDateString('en-US', { weekday: 'short' }),
        patients: day.total_patients,
        respiratory: day.breakdown?.respiratory || 0
    }));

    // Calculate metrics
    const peakLoad = Math.max(...data.map(d => d.total_patients));
    const avgRespiratory = Math.round(
        data.reduce((sum, d) => sum + (d.breakdown?.respiratory || 0), 0) / data.length
    );

    // Custom tooltip
    const CustomTooltip = ({ active, payload }) => {
        if (active && payload && payload.length) {
            return (
                <div className="chart-tooltip">
                    <p className="tooltip-label">{payload[0].payload.date}</p>
                    <p className="tooltip-value">
                        Total: <strong>{payload[0].value}</strong> patients
                    </p>
                    <p className="tooltip-value-secondary">
                        Respiratory: {payload[0].payload.respiratory}
                    </p>
                </div>
            );
        }
        return null;
    };

    return (
        <div className="card">
            <h3 className="card-title">7-Day Patient Forecast</h3>

            {/* Chart */}
            <div className="chart-container">
                <ResponsiveContainer width="100%" height={220}>
                    <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                        <XAxis
                            dataKey="date"
                            tick={{ fill: '#6B7280', fontSize: 12 }}
                            axisLine={{ stroke: '#E5E7EB' }}
                        />
                        <YAxis
                            tick={{ fill: '#6B7280', fontSize: 12 }}
                            axisLine={{ stroke: '#E5E7EB' }}
                        />
                        <Tooltip content={<CustomTooltip />} />
                        <Bar
                            dataKey="patients"
                            fill="#769DD7"
                            radius={[4, 4, 0, 0]}
                            maxBarSize={50}
                        />
                    </BarChart>
                </ResponsiveContainer>
            </div>

            {/* Metrics */}
            <div className="forecast-metrics">
                <div className="metric">
                    <span className="metric-label">Peak Load</span>
                    <span className="metric-value">{peakLoad}</span>
                </div>
                <div className="metric-divider"></div>
                <div className="metric">
                    <span className="metric-label">Avg Respiratory</span>
                    <span className="metric-value">{avgRespiratory}</span>
                </div>
            </div>
        </div>
    );
};

export default SevenDayForecastCard;
