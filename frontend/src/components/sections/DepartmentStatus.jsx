import { Card } from "@/components/ui/card";
import { useEffect, useState } from "react";
import axios from "axios";
import { createClient } from '@supabase/supabase-js';

interface DepartmentData {
  name: string;
  occupancy: number;
}

export const DepartmentStatus = () => {
  const [departments, setDepartments] = useState<DepartmentData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Optional: Supabase client for realtime updates
  const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
  const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY;
  const supabase = supabaseUrl && supabaseKey ? createClient(supabaseUrl, supabaseKey) : null;

  useEffect(() => {
    const fetchDepartmentStatus = async () => {
      try {
        const response = await axios.get('http://localhost:5000/api/department-status');
        setDepartments(response.data);
        setError(null);
      } catch (err) {
        console.error('Error fetching department status:', err);
        setError('Failed to load department data');
        // Fallback to static data
        setDepartments([
          { name: "Emergency", occupancy: 85 },
          { name: "ICU", occupancy: 92 },
          { name: "Surgery", occupancy: 71 },
          { name: "Pediatrics", occupancy: 54 },
          { name: "General Ward", occupancy: 67 }
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchDepartmentStatus();

    // Optional: Set up realtime subscription
    if (supabase) {
      const channel = supabase
        .channel('department_status_changes')
        .on('postgres_changes',
          { event: '*', schema: 'public', table: 'department_status' },
          (payload) => {
            console.log('Realtime update:', payload);
            fetchDepartmentStatus(); // Refresh data on changes
          }
        )
        .subscribe();

      return () => {
        supabase.removeChannel(channel);
      };
    }

    // Refresh data every 60 seconds if no realtime
    const interval = setInterval(fetchDepartmentStatus, 60000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (occupancy: number) => {
    if (occupancy >= 85) return 'bg-red-500'; // Critical - Red
    if (occupancy >= 65) return 'bg-yellow-500'; // Warning - Yellow
    return 'bg-green-500'; // Stable - Green
  };

  const getStatusText = (occupancy: number) => {
    if (occupancy >= 85) return 'Critical';
    if (occupancy >= 65) return 'Warning';
    return 'Stable';
  };

  if (loading) {
    return (
      <Card className="p-6 shadow-soft">
        <h3 className="text-lg font-semibold text-foreground mb-4">Department Status</h3>
        <p className="text-muted-foreground">Loading department data...</p>
      </Card>
    );
  }

  return (
    <Card className="p-6 shadow-soft">
      <h3 className="text-lg font-semibold text-foreground mb-4">Department Status</h3>
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
          <p className="text-red-600 text-sm">{error}. Showing cached data.</p>
        </div>
      )}
      <div className="space-y-4">
        {departments.map((dept) => (
          <div key={dept.name} className="flex items-center gap-4">
            <div className="flex-1">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-foreground">{dept.name}</span>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-muted-foreground">{dept.occupancy}%</span>
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    dept.occupancy >= 85 ? 'bg-red-100 text-red-700' :
                    dept.occupancy >= 65 ? 'bg-yellow-100 text-yellow-700' :
                    'bg-green-100 text-green-700'
                  }`}>
                    {getStatusText(dept.occupancy)}
                  </span>
                </div>
              </div>
              <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${getStatusColor(dept.occupancy)}`}
                  style={{ width: `${dept.occupancy}%` }}
                />
              </div>
            </div>
          </div>
        ))}
      </div>
      {supabase && (
        <p className="text-xs text-muted-foreground mt-4">
          Real-time updates enabled
        </p>
      )}
    </Card>
  );
};
