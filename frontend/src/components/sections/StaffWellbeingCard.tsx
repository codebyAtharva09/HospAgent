import React from 'react';

const StaffWellbeingCard = ({ riskData }) => {
    // Handle missing or loading data
    if (!riskData) {
        return (
            <div className="card wellbeing-card">
                <h3 className="card-title">Staff Wellbeing</h3>
                <div className="wellbeing-loading">
                    <span className="loading-text">Loading wellbeing data...</span>
                </div>
            </div>
        );
    }

    // Extract burnout data from risk object
    const burnoutCount = riskData.burnout_high_count || 0;
    const burnoutNote = riskData.burnout_note;

    // Determine message
    let message;
    if (burnoutNote) {
        // Use custom note from backend if provided
        message = burnoutNote;
    } else if (burnoutCount > 0) {
        // Generate message based on count
        message = `${burnoutCount} staff member${burnoutCount > 1 ? 's' : ''} at high burnout risk`;
    } else {
        // All clear
        message = 'No staff at high burnout risk';
    }

    // Determine alert status
    const isAlert = burnoutCount > 0;

    return (
        <div className="card wellbeing-card">
            <h3 className="card-title">Staff Wellbeing</h3>

            <div className={`wellbeing-status ${isAlert ? 'alert' : 'ok'}`}>
                <span className="wellbeing-icon">
                    {isAlert ? '⚠️' : '✅'}
                </span>
                <div className="wellbeing-content">
                    <span className="wellbeing-message">{message}</span>
                    {isAlert && burnoutCount > 0 && (
                        <span className="wellbeing-count">{burnoutCount} affected</span>
                    )}
                </div>
            </div>

            {/* Additional context if available */}
            {isAlert && (
                <div className="wellbeing-action">
                    <span className="action-label">Recommended Action:</span>
                    <span className="action-text">Review shift schedules and consider additional support</span>
                </div>
            )}
        </div>
    );
};

export default StaffWellbeingCard;
