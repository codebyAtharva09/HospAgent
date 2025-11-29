import React, { useEffect, useState } from 'react';
import { hospitalOps, Patient, PatientAdmissionRequest } from '../api/hospitalOps';
import { UserPlus, LogOut, Activity, Search, AlertCircle } from 'lucide-react';

const DEPARTMENTS = ["Cardiology", "Neurology", "Orthopedics", "General Medicine", "Pediatrics", "Emergency"];
const DOCTORS = [
    { id: "DOC-001", name: "Dr. Mehta", dept: "Cardiology" },
    { id: "DOC-002", name: "Dr. Gupta", dept: "Neurology" },
    { id: "DOC-003", name: "Dr. Khan", dept: "Orthopedics" },
    { id: "DOC-004", name: "Dr. Sarah", dept: "General Medicine" },
    { id: "DOC-005", name: "Dr. Patel", dept: "Pediatrics" },
    { id: "DOC-006", name: "Dr. Rao", dept: "Emergency" }
];

const ReceptionView = () => {
    const [patients, setPatients] = useState<Patient[]>([]);
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Form State
    const [formData, setFormData] = useState<PatientAdmissionRequest>({
        name: '',
        age: 0,
        gender: 'Male',
        contact: '',
        address: '',
        doctor_id: '',
        doctor_name: '',
        department: '',
        reason: '',
        bed_type: 'General Ward'
    });

    const fetchPatients = async () => {
        try {
            setLoading(true);
            const data = await hospitalOps.getPatients('ADMITTED');
            setPatients(data);
        } catch (err) {
            console.error(err);
            setError("Failed to load patients");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchPatients();
    }, []);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: name === 'age' ? parseInt(value) || 0 : value
        }));

        // Auto-fill doctor name if doctor_id changes
        if (name === 'doctor_id') {
            const doc = DOCTORS.find(d => d.id === value);
            if (doc) {
                setFormData(prev => ({ ...prev, doctor_name: doc.name, department: doc.dept, doctor_id: value }));
            }
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSubmitting(true);
        try {
            await hospitalOps.admitPatient(formData);
            // Reset form
            setFormData({
                name: '', age: 0, gender: 'Male', contact: '', address: '',
                doctor_id: '', doctor_name: '', department: '', reason: '', bed_type: 'General Ward'
            });
            fetchPatients();
            alert("Patient admitted successfully!");
        } catch (err) {
            alert("Failed to admit patient");
        } finally {
            setSubmitting(false);
        }
    };

    const handleDischarge = async (id: string) => {
        if (!confirm("Are you sure you want to discharge this patient?")) return;
        try {
            await hospitalOps.dischargePatient(id);
            fetchPatients();
        } catch (err) {
            alert("Failed to discharge patient");
        }
    };

    return (
        <div className="space-y-6">
            {/* Header & Banner */}
            <div>
                <h2 className="text-2xl font-bold text-slate-800">Reception & Appointments</h2>
                <div className="mt-2 bg-blue-50 p-4 rounded-xl border border-blue-100 flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5" />
                    <p className="text-sm text-blue-800">
                        Patient check-in and appointment scheduling tools are live here.
                        For current bed availability and surge risk, refer to the Command Center dashboard.
                    </p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Admission Form */}
                <div className="lg:col-span-1">
                    <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                        <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
                            <UserPlus className="w-5 h-5 text-blue-500" />
                            New Admission
                        </h3>
                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div>
                                <label className="block text-xs font-medium text-slate-500 mb-1">Patient Name</label>
                                <input required name="name" value={formData.name} onChange={handleInputChange} className="w-full p-2 border rounded-lg text-sm" placeholder="Full Name" />
                            </div>
                            <div className="grid grid-cols-2 gap-3">
                                <div>
                                    <label className="block text-xs font-medium text-slate-500 mb-1">Age</label>
                                    <input required type="number" name="age" value={formData.age || ''} onChange={handleInputChange} className="w-full p-2 border rounded-lg text-sm" placeholder="Age" />
                                </div>
                                <div>
                                    <label className="block text-xs font-medium text-slate-500 mb-1">Gender</label>
                                    <select name="gender" value={formData.gender} onChange={handleInputChange} className="w-full p-2 border rounded-lg text-sm">
                                        <option>Male</option>
                                        <option>Female</option>
                                        <option>Other</option>
                                    </select>
                                </div>
                            </div>
                            <div>
                                <label className="block text-xs font-medium text-slate-500 mb-1">Contact</label>
                                <input required name="contact" value={formData.contact} onChange={handleInputChange} className="w-full p-2 border rounded-lg text-sm" placeholder="Phone Number" />
                            </div>
                            <div>
                                <label className="block text-xs font-medium text-slate-500 mb-1">Address</label>
                                <input required name="address" value={formData.address} onChange={handleInputChange} className="w-full p-2 border rounded-lg text-sm" placeholder="City, Area" />
                            </div>

                            <div className="border-t pt-2 mt-2">
                                <label className="block text-xs font-medium text-slate-500 mb-1">Assign Doctor</label>
                                <select required name="doctor_id" value={formData.doctor_id} onChange={handleInputChange} className="w-full p-2 border rounded-lg text-sm mb-2">
                                    <option value="">Select Doctor</option>
                                    {DOCTORS.map(d => <option key={d.id} value={d.id}>{d.name} ({d.dept})</option>)}
                                </select>
                            </div>

                            <div>
                                <label className="block text-xs font-medium text-slate-500 mb-1">Reason / Complaint</label>
                                <textarea required name="reason" value={formData.reason} onChange={handleInputChange} className="w-full p-2 border rounded-lg text-sm" rows={2} placeholder="Symptoms..." />
                            </div>

                            <div>
                                <label className="block text-xs font-medium text-slate-500 mb-1">Bed Type</label>
                                <select name="bed_type" value={formData.bed_type} onChange={handleInputChange} className="w-full p-2 border rounded-lg text-sm">
                                    <option>General Ward</option>
                                    <option>ICU</option>
                                    <option>Emergency</option>
                                </select>
                            </div>

                            <button type="submit" disabled={submitting} className="w-full bg-blue-600 text-white py-2 rounded-lg font-medium hover:bg-blue-700 transition disabled:opacity-50">
                                {submitting ? 'Admitting...' : 'Admit Patient'}
                            </button>
                        </form>
                    </div>
                </div>

                {/* Active Admissions List */}
                <div className="lg:col-span-2">
                    <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm h-full">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2">
                                <Activity className="w-5 h-5 text-emerald-500" />
                                Active Admissions
                            </h3>
                            <span className="bg-emerald-100 text-emerald-700 px-2 py-1 rounded-full text-xs font-bold">
                                {patients.length} Active
                            </span>
                        </div>

                        {loading ? (
                            <div className="text-center py-10 text-slate-400">Loading patients...</div>
                        ) : patients.length === 0 ? (
                            <div className="text-center py-10 text-slate-400 bg-slate-50 rounded-lg border border-dashed border-slate-200">
                                No active admissions found.
                            </div>
                        ) : (
                            <div className="overflow-x-auto">
                                <table className="w-full text-sm text-left">
                                    <thead className="bg-slate-50 text-slate-500 font-medium">
                                        <tr>
                                            <th className="px-4 py-3 rounded-l-lg">Patient</th>
                                            <th className="px-4 py-3">Doctor / Dept</th>
                                            <th className="px-4 py-3">Admitted</th>
                                            <th className="px-4 py-3">Bed</th>
                                            <th className="px-4 py-3 rounded-r-lg text-right">Action</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-slate-100">
                                        {patients.map(p => (
                                            <tr key={p.id} className="hover:bg-slate-50">
                                                <td className="px-4 py-3">
                                                    <div className="font-medium text-slate-800">{p.name}</div>
                                                    <div className="text-xs text-slate-500">{p.age}y / {p.gender}</div>
                                                </td>
                                                <td className="px-4 py-3">
                                                    <div className="text-slate-800">{p.doctor_name}</div>
                                                    <div className="text-xs text-slate-500">{p.department}</div>
                                                </td>
                                                <td className="px-4 py-3 text-slate-600">
                                                    {new Date(p.admitted_at).toLocaleDateString()}
                                                    <div className="text-xs text-slate-400">{new Date(p.admitted_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
                                                </td>
                                                <td className="px-4 py-3">
                                                    <span className="bg-blue-50 text-blue-700 px-2 py-1 rounded text-xs">
                                                        {p.bed_type || 'General'}
                                                    </span>
                                                </td>
                                                <td className="px-4 py-3 text-right">
                                                    <button
                                                        onClick={() => handleDischarge(p.id)}
                                                        className="text-red-600 hover:bg-red-50 px-3 py-1 rounded-lg text-xs font-medium border border-red-200 transition"
                                                    >
                                                        Discharge
                                                    </button>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ReceptionView;
