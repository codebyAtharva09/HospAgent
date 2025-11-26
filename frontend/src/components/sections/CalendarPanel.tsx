import React, { useState, useEffect } from 'react';

interface Props {
    festivals?: any[];
}

const CalendarPanel: React.FC<Props> = ({ festivals = [] }) => {

    return (
        <div className="card" style={{ height: '100%' }}>
            <h3 className="card-title" style={{ display: 'flex', alignItems: 'center' }}>
                <span style={{ marginRight: '0.5rem' }}>📅</span> Upcoming Festivals
            </h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {festivals.length === 0 ? (
                    <p style={{ color: '#9CA3AF', fontSize: '0.875rem' }}>No upcoming festivals detected.</p>
                ) : (
                    festivals.map((fest, idx) => (
                        <div
                            key={idx}
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'space-between',
                                padding: '0.75rem',
                                borderRadius: '8px',
                                border: fest.is_high_risk ? '1px solid #FFEDD5' : '1px solid #F1F5F9',
                                backgroundColor: fest.is_high_risk ? '#FFF7ED' : '#F8FAFC'
                            }}
                        >
                            <div style={{ display: 'flex', alignItems: 'center' }}>
                                <div style={{
                                    width: '8px',
                                    height: '8px',
                                    borderRadius: '50%',
                                    marginRight: '0.75rem',
                                    backgroundColor: fest.is_high_risk ? '#F97316' : '#60A5FA'
                                }}></div>
                                <div>
                                    <p style={{ fontWeight: 500, fontSize: '0.875rem', color: '#1E293B' }}>{fest.name}</p>
                                    <p style={{ fontSize: '0.75rem', color: '#64748B' }}>{new Date(fest.date).toLocaleDateString()}</p>
                                </div>
                            </div>
                            {fest.is_high_risk && (
                                <span style={{
                                    padding: '0.25rem 0.5rem',
                                    fontSize: '0.625rem',
                                    fontWeight: 700,
                                    color: '#EA580C',
                                    backgroundColor: '#FFEDD5',
                                    borderRadius: '9999px'
                                }}>
                                    HIGH RISK
                                </span>
                            )}
                        </div>
                    ))
                )}
            </div>

            <div style={{ marginTop: '1.5rem', paddingTop: '1rem', borderTop: '1px solid #F1F5F9' }}>
                <p style={{ fontSize: '0.75rem', color: '#9CA3AF' }}>
                    *Synced with Google Calendar (Indian Holidays)
                </p>
            </div>
        </div>
    );
};

export default CalendarPanel;
