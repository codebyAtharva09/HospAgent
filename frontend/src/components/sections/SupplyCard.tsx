import React from 'react';

const SupplyCard = ({ supplyPlan }) => {
    if (!supplyPlan || supplyPlan.length === 0) return null;

    // Helper to get color based on status
    const getStatusStyle = (status) => {
        switch (status) {
            case 'OK': return { bg: '#DCFCE7', text: '#15803D' };
            case 'MEDIUM': return { bg: '#FEF9C3', text: '#A16207' };
            case 'LOW': return { bg: '#FEE2E2', text: '#991B1B' };
            default: return { bg: '#F3F4F6', text: '#4B5563' };
        }
    };

    return (
        <div className="card">
            <h3 className="card-title">Critical Supplies</h3>

            <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', fontSize: '0.875rem', textAlign: 'left', borderCollapse: 'collapse' }}>
                    <thead style={{ fontSize: '0.75rem', color: '#64748B', textTransform: 'uppercase', backgroundColor: '#F8FAFC' }}>
                        <tr>
                            <th style={{ padding: '0.5rem 0.75rem' }}>Item</th>
                            <th style={{ padding: '0.5rem 0.75rem' }}>Required</th>
                            <th style={{ padding: '0.5rem 0.75rem' }}>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {supplyPlan.map((supply, idx) => {
                            const style = getStatusStyle(supply.status);
                            return (
                                <tr key={idx} style={{ borderBottom: '1px solid #F1F5F9' }}>
                                    <td style={{ padding: '0.5rem 0.75rem', fontWeight: 500 }}>{supply.item}</td>
                                    <td style={{ padding: '0.5rem 0.75rem' }}>{supply.required}</td>
                                    <td style={{ padding: '0.5rem 0.75rem' }}>
                                        <span style={{
                                            padding: '0.25rem 0.5rem',
                                            backgroundColor: style.bg,
                                            color: style.text,
                                            borderRadius: '9999px',
                                            fontSize: '0.625rem',
                                            fontWeight: 700
                                        }}>
                                            {supply.status}
                                        </span>
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>

            {/* Show notes from the first LOW status item, or just the first item's note if available */}
            {supplyPlan.some(s => s.notes) && (
                <div style={{ marginTop: '1rem', fontSize: '0.75rem', color: '#64748B', fontStyle: 'italic' }}>
                    Action: {supplyPlan.find(s => s.status === 'LOW')?.notes || supplyPlan[0].notes}
                </div>
            )}
        </div>
    );
};

export default SupplyCard;
