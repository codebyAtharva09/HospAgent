import { Card } from "@/components/ui/card";
import { useEffect, useState } from "react";
import api from "@/services/api";

import { Building2, Users } from "lucide-react";

export const DepartmentStatus = () => {
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);



  useEffect(() => {
    const fetchDepartmentStatus = async () => {
      try {
        const response = await api.get('/department-status');
        setDepartments(response.data);
        setError(null);
      } catch (err) {
        console.error('Error fetching department status:', err);
        setError('Failed to load department status');
        // Fallback data
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

  }, []);

  if (loading) return <div className="p-4 text-muted-foreground animate-pulse">Loading status...</div>;
  if (error) return <div className="p-4 text-rose-500 bg-rose-500/10 rounded-lg border border-rose-500/20">{error}</div>;

  return (
    <Card className="p-6 backdrop-blur-md bg-white/5 border-white/10 shadow-xl hover:bg-white/10 transition-all duration-300">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <Building2 className="h-5 w-5 text-pink-500" />
          Department Load
        </h3>
        <div className="flex items-center gap-2">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-pink-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-pink-500"></span>
          </span>
          <span className="text-xs font-medium text-pink-500">Live</span>
        </div>
      </div>

      <div className="space-y-4">
        {departments.map((dept) => (
          <div key={dept.name} className="group">
            <div className="flex justify-between items-center mb-2">
              <span className="font-medium flex items-center gap-2 text-sm">
                <div className={`w-2 h-2 rounded-full ${dept.occupancy > 90 ? 'bg-rose-500 shadow-lg shadow-rose-500/50' :
                  dept.occupancy > 75 ? 'bg-amber-500 shadow-lg shadow-amber-500/50' : 'bg-emerald-500 shadow-lg shadow-emerald-500/50'
                  }`} />
                {dept.name}
              </span>
              <span className={`text-sm font-bold ${dept.occupancy > 90 ? 'text-rose-500' :
                dept.occupancy > 75 ? 'text-amber-500' : 'text-emerald-500'
                }`}>
                {dept.occupancy}%
              </span>
            </div>
            <div className="w-full bg-white/5 rounded-full h-2.5 overflow-hidden backdrop-blur-sm">
              <div
                className={`h-full rounded-full transition-all duration-500 ${dept.occupancy > 90 ? 'bg-gradient-to-r from-rose-500 to-rose-600' :
                  dept.occupancy > 75 ? 'bg-gradient-to-r from-amber-500 to-amber-600' : 'bg-gradient-to-r from-emerald-500 to-emerald-600'
                  } group-hover:shadow-lg ${dept.occupancy > 90 ? 'group-hover:shadow-rose-500/50' :
                    dept.occupancy > 75 ? 'group-hover:shadow-amber-500/50' : 'group-hover:shadow-emerald-500/50'
                  }`}
                style={{ width: `${dept.occupancy}%` }}
              ></div>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
};
