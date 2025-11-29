import React, { useEffect, useState } from 'react';
import { hospitalOps, Supply } from '../api/hospitalOps';
import { useAuth } from '../context/AuthContext';
import { Package, AlertTriangle, RefreshCw, CheckCircle, Plus, Search } from 'lucide-react';

const PharmacyView = () => {
    const { user } = useAuth();
    const [supplies, setSupplies] = useState<Supply[]>([]);
    const [loading, setLoading] = useState(true);
    const [restockQty, setRestockQty] = useState<{ [key: string]: number }>({});
    const [submitting, setSubmitting] = useState<string | null>(null);

    const fetchData = async () => {
        try {
            setLoading(true);
            const data = await hospitalOps.getSupplies();
            setSupplies(data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const handleRestock = async (supply: Supply) => {
        const qty = restockQty[supply.id];
        if (!qty || qty <= 0) return;

        setSubmitting(supply.id);
        try {
            await hospitalOps.restockSupply(supply.id, qty);
            await fetchData(); // Refresh
            setRestockQty(prev => ({ ...prev, [supply.id]: 0 })); // Reset input
            alert(`Restocked ${supply.name} by ${qty} units.`);
        } catch (err) {
            alert("Failed to restock supply");
        } finally {
            setSubmitting(null);
        }
    };

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold text-slate-800">Pharmacy & Inventory Management</h2>
                <p className="text-slate-500">
                    This page represents the <strong>Pharmacy & Inventory Management</strong> console, where the pharmacist monitors stock, raises reorder requests, and collaborates with the Super Admin to keep critical supplies available.
                </p>
            </div>

            <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                <div className="p-6 border-b border-slate-100 flex justify-between items-center">
                    <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2">
                        <Package className="w-5 h-5 text-blue-500" />
                        Critical Supplies Inventory
                    </h3>
                    <button onClick={fetchData} className="p-2 hover:bg-slate-50 rounded-full text-slate-400">
                        <RefreshCw className="w-4 h-4" />
                    </button>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full text-sm text-left">
                        <thead className="bg-slate-50 text-slate-500 font-medium">
                            <tr>
                                <th className="px-6 py-3">Item Name</th>
                                <th className="px-6 py-3">Current Stock</th>
                                <th className="px-6 py-3">Status</th>
                                <th className="px-6 py-3">Quick Restock</th>
                                <th className="px-6 py-3 text-right">Action</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                            {supplies.map(item => (
                                <tr key={item.id} className={`hover:bg-slate-50 ${item.status !== 'OK' ? 'bg-red-50/30' : ''}`}>
                                    <td className="px-6 py-4 font-medium text-slate-800">{item.name}</td>
                                    <td className="px-6 py-4">
                                        <div className="flex items-center gap-2">
                                            <span className="font-bold text-lg">{item.current_stock}</span>
                                            <span className="text-xs text-slate-400">{item.unit}</span>
                                        </div>
                                        <div className="text-xs text-slate-400 mt-0.5">
                                            Threshold: {item.reorder_threshold}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        {item.status === 'CRITICAL' && (
                                            <span className="inline-flex items-center gap-1 bg-red-100 text-red-700 px-2 py-1 rounded-full text-xs font-bold animate-pulse">
                                                <AlertTriangle className="w-3 h-3" /> Critical
                                            </span>
                                        )}
                                        {item.status === 'LOW' && (
                                            <span className="inline-flex items-center gap-1 bg-amber-100 text-amber-700 px-2 py-1 rounded-full text-xs font-bold">
                                                <AlertTriangle className="w-3 h-3" /> Low
                                            </span>
                                        )}
                                        {item.status === 'OK' && (
                                            <span className="inline-flex items-center gap-1 bg-emerald-100 text-emerald-700 px-2 py-1 rounded-full text-xs font-bold">
                                                <CheckCircle className="w-3 h-3" /> OK
                                            </span>
                                        )}
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="flex items-center gap-2">
                                            <input
                                                type="number"
                                                min="1"
                                                placeholder="+ Qty"
                                                className="w-24 p-2 border rounded-lg text-sm"
                                                value={restockQty[item.id] || ''}
                                                onChange={(e) => setRestockQty(prev => ({ ...prev, [item.id]: parseInt(e.target.value) }))}
                                            />
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-right">
                                        <button
                                            onClick={() => handleRestock(item)}
                                            disabled={!restockQty[item.id] || submitting === item.id}
                                            className="bg-blue-600 text-white hover:bg-blue-700 px-4 py-2 rounded-lg text-xs font-bold transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 ml-auto"
                                        >
                                            {submitting === item.id ? '...' : <><Plus className="w-3 h-3" /> Restock</>}
                                        </button>
                                    </td>
                                </tr>
                            ))}
                            {supplies.length === 0 && !loading && (
                                <tr><td colSpan={5} className="px-6 py-8 text-center text-slate-400">No supplies data found.</td></tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default PharmacyView;
