import React from 'react';

const StaffCard = ({ staffingPlan }) => {
    if (!staffingPlan || staffingPlan.length === 0) return null;

    // Backend returns a list where the first item is the summary for "Hospital Wide"
    const hospitalWide = staffingPlan.find(p => p.department === "Hospital Wide") || staffingPlan[0] || {};

    return (
        <div className="card">
            <h3 className="card-title">Staffing Recommendations</h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '0.75rem',
                    backgroundColor: '#EFF6FF',
                    borderRadius: '8px',
                    border: '1px solid #DBEAFE'
                }}>
                    <div style={{ display: 'flex', alignItems: 'center' }}>
                        <span style={{ fontSize: '1.5rem', marginRight: '0.75rem' }}>👨‍⚕️</span>
                        <div>
                            <p style={{ fontSize: '0.875rem', fontWeight: 700, color: '#334155' }}>Doctors</p>
                            <p style={{ fontSize: '0.75rem', color: '#64748B' }}>Required Today</p>
                        </div>
                    </div>
                    <span style={{ fontSize: '1.25rem', fontWeight: 700, color: '#769DD7' }}>{hospitalWide.doctors || 0}</span>
                </div>

                <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '0.75rem',
                    backgroundColor: '#EFF6FF',
                    borderRadius: '8px',
                    border: '1px solid #DBEAFE'
                }}>
                    <div style={{ display: 'flex', alignItems: 'center' }}>
                        <span style={{ fontSize: '1.5rem', marginRight: '0.75rem' }}>👩‍⚕️</span>
                        <div>
                            <p style={{ fontSize: '0.875rem', fontWeight: 700, color: '#334155' }}>Nurses</p>
                            <p style={{ fontSize: '0.75rem', color: '#64748B' }}>Required Today</p>
                        </div>
                    </div>
                    <span style={{ fontSize: '1.25rem', fontWeight: 700, color: '#769DD7' }}>{hospitalWide.nurses || 0}</span>
                </div>
            </div>

            {hospitalWide.notes && hospitalWide.notes.length > 0 && (
                <div style={{
                    marginTop: '1rem',
                    padding: '0.75rem',
                    backgroundColor: '#FEF2F2',
                    border: '1px solid #FEE2E2',
                    borderRadius: '8px'
                }}>
                    <p style={{ fontSize: '0.75rem', fontWeight: 700, color: '#DC2626', marginBottom: '0.25rem' }}>⚠️ NOTES</p>
                    {hospitalWide.notes.map((note, idx) => (
                        <p key={idx} style={{ fontSize: '0.75rem', color: '#EF4444' }}>• {note}</p>
                    ))}
                </div>
            )}
        </div>
    );
};

export default StaffCard;
