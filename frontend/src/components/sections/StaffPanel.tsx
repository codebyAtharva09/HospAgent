import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { UserCheck, AlertTriangle, CheckCircle, Clock } from "lucide-react";
import { useState, useEffect } from "react";

const StaffPanel = () => {
  const [staffData, setStaffData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStaffData = async () => {
      try {
        setError(null);
        const response = await fetch('http://localhost:5000/api/staff');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setStaffData(data);
      } catch (err) {
        console.error('Error fetching staff data:', err);
        setError('Failed to load staff data. Please check if the backend is running.');
      } finally {
        setLoading(false);
      }
    };

    fetchStaffData();
    const interval = setInterval(fetchStaffData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="p-6 bg-white rounded-2xl shadow-lg">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="h-64 bg-gray-200 rounded mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-20 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-white rounded-2xl shadow-lg">
        <div className="text-center py-12">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Connection Error</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">👥 Staff Allocation</h2>
          <p className="text-gray-600">AI-optimized staffing recommendations</p>
        </div>
        <Button className="bg-blue-500 hover:bg-blue-600 text-white shadow-md">
          <UserCheck size={18} className="mr-2" />
          Apply AI Recommendations
        </Button>
      </div>

      {/* Staff Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-6 bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Doctors</p>
              <p className="text-2xl font-bold text-gray-900">{staffData.doctors.on_duty}/{staffData.doctors.total}</p>
              <p className="text-xs text-gray-500">On Duty / Total</p>
            </div>
            <div className={`p-2 rounded-full ${staffData.doctors.on_duty >= staffData.doctors.recommended ? 'bg-green-100' : 'bg-red-100'}`}>
              <UserCheck className={`w-6 h-6 ${staffData.doctors.on_duty >= staffData.doctors.recommended ? 'text-green-600' : 'text-red-600'}`} />
            </div>
          </div>
        </Card>

        <Card className="p-6 bg-gradient-to-br from-green-50 to-emerald-50 border-green-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Nurses</p>
              <p className="text-2xl font-bold text-gray-900">{staffData.nurses.on_duty}/{staffData.nurses.total}</p>
              <p className="text-xs text-gray-500">On Duty / Total</p>
            </div>
            <div className={`p-2 rounded-full ${staffData.nurses.on_duty >= staffData.nurses.recommended ? 'bg-green-100' : 'bg-red-100'}`}>
              <UserCheck className={`w-6 h-6 ${staffData.nurses.on_duty >= staffData.nurses.recommended ? 'text-green-600' : 'text-red-600'}`} />
            </div>
          </div>
        </Card>

        <Card className="p-6 bg-gradient-to-br from-purple-50 to-violet-50 border-purple-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Technicians</p>
              <p className="text-2xl font-bold text-gray-900">{staffData.technicians.on_duty}/{staffData.technicians.total}</p>
              <p className="text-xs text-gray-500">On Duty / Total</p>
            </div>
            <div className={`p-2 rounded-full ${staffData.technicians.on_duty >= staffData.technicians.recommended ? 'bg-green-100' : 'bg-red-100'}`}>
              <UserCheck className={`w-6 h-6 ${staffData.technicians.on_duty >= staffData.technicians.recommended ? 'text-green-600' : 'text-red-600'}`} />
            </div>
          </div>
        </Card>
      </div>

      {/* Department Allocation Table */}
      <Card className="shadow-lg overflow-hidden">
        <div className="px-6 py-4 bg-gray-50 border-b">
          <h3 className="text-lg font-semibold text-gray-900">Department-wise Allocation</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-100">
              <tr>
                <th className="text-left p-4 text-sm font-semibold text-gray-700">Department</th>
                <th className="text-center p-4 text-sm font-semibold text-gray-700">Doctors</th>
                <th className="text-center p-4 text-sm font-semibold text-gray-700">Nurses</th>
                <th className="text-center p-4 text-sm font-semibold text-gray-700">Technicians</th>
                <th className="text-center p-4 text-sm font-semibold text-gray-700">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {staffData.allocation.map((dept, index) => {
                const totalStaff = dept.doctors + dept.nurses + dept.technicians;
                const isAdequate = totalStaff >= 40; // Simple threshold

                return (
                  <tr key={index} className="hover:bg-gray-50 transition-colors">
                    <td className="p-4">
                      <span className="font-medium text-gray-900">{dept.department}</span>
                    </td>
                    <td className="p-4 text-center">
                      <span className="text-gray-900 font-semibold">{dept.doctors}</span>
                    </td>
                    <td className="p-4 text-center">
                      <span className="text-gray-900 font-semibold">{dept.nurses}</span>
                    </td>
                    <td className="p-4 text-center">
                      <span className="text-gray-900 font-semibold">{dept.technicians}</span>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center justify-center">
                        <Badge variant="outline" className={`${isAdequate ? 'bg-green-100 text-green-800 border-green-200' : 'bg-red-100 text-red-800 border-red-200'}`}>
                          {isAdequate ? <CheckCircle size={12} className="mr-1" /> : <AlertTriangle size={12} className="mr-1" />}
                          {isAdequate ? 'Adequate' : 'Needs Attention'}
                        </Badge>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </Card>

      <div className="text-center">
        <p className="text-xs text-gray-500">
          Data refreshes every 30 seconds • AI-powered recommendations
        </p>
      </div>
    </div>
  );
};

export { StaffPanel };
