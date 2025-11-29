import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Save, Bell, Mail, MessageSquare } from 'lucide-react';

interface NotificationConfig {
    critical_supply_emails: string[];
    critical_supply_sms: string[];
    high_risk_emails: string[];
    high_risk_sms: string[];
    festival_surge_emails: string[];
    festival_surge_sms: string[];
}

const NotificationSettings = () => {
    const [config, setConfig] = useState<NotificationConfig>({
        critical_supply_emails: [],
        critical_supply_sms: [],
        high_risk_emails: [],
        high_risk_sms: [],
        festival_surge_emails: [],
        festival_surge_sms: []
    });
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const { token } = useAuth();

    useEffect(() => {
        const fetchConfig = async () => {
            try {
                const res = await fetch('/api/admin/notification-config', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (res.ok) {
                    setConfig(await res.json());
                }
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchConfig();
    }, [token]);

    const handleSave = async () => {
        setSaving(true);
        try {
            await fetch('/api/admin/notification-config', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(config)
            });
            alert('Settings saved successfully!');
        } catch (err) {
            console.error(err);
            alert('Failed to save settings.');
        } finally {
            setSaving(false);
        }
    };

    const updateField = (field: keyof NotificationConfig, value: string) => {
        // Split by comma and trim
        const array = value.split(',').map(s => s.trim()).filter(s => s);
        setConfig({ ...config, [field]: array });
    };

    const renderSection = (title: string, emailField: keyof NotificationConfig, smsField: keyof NotificationConfig) => (
        <div className="bg-white rounded-xl border border-slate-200 p-6">
            <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
                <Bell className="w-5 h-5 text-blue-500" />
                {title}
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2 flex items-center gap-2">
                        <Mail className="w-4 h-4" /> Email Recipients
                    </label>
                    <textarea
                        className="w-full border border-slate-300 rounded-lg p-3 text-sm h-24 focus:ring-2 focus:ring-blue-500 outline-none"
                        placeholder="email@example.com, admin@hospital.com"
                        value={config[emailField].join(', ')}
                        onChange={e => updateField(emailField, e.target.value)}
                    />
                    <p className="text-xs text-slate-500 mt-1">Comma separated email addresses</p>
                </div>
                <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2 flex items-center gap-2">
                        <MessageSquare className="w-4 h-4" /> SMS Recipients
                    </label>
                    <textarea
                        className="w-full border border-slate-300 rounded-lg p-3 text-sm h-24 focus:ring-2 focus:ring-blue-500 outline-none"
                        placeholder="+1234567890, +9876543210"
                        value={config[smsField].join(', ')}
                        onChange={e => updateField(smsField, e.target.value)}
                    />
                    <p className="text-xs text-slate-500 mt-1">Comma separated phone numbers with country code</p>
                </div>
            </div>
        </div>
    );

    if (loading) return <div>Loading...</div>;

    return (
        <div className="space-y-6 max-w-4xl">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-2xl font-bold text-slate-800">Notification Settings</h2>
                    <p className="text-slate-500">Configure who receives critical alerts.</p>
                </div>
                <button
                    onClick={handleSave}
                    disabled={saving}
                    className="bg-blue-600 text-white px-6 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700 disabled:opacity-50"
                >
                    <Save className="w-4 h-4" />
                    {saving ? 'Saving...' : 'Save Changes'}
                </button>
            </div>

            <div className="space-y-6">
                {renderSection('High Risk & Epidemic Alerts', 'high_risk_emails', 'high_risk_sms')}
                {renderSection('Critical Supply Alerts', 'critical_supply_emails', 'critical_supply_sms')}
                {renderSection('Festival Surge Alerts', 'festival_surge_emails', 'festival_surge_sms')}
            </div>
        </div>
    );
};

export default NotificationSettings;
