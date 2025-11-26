import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Users, UserCheck, AlertTriangle, CheckCircle } from "lucide-react";
import api from "@/services/api";

interface StaffCategory {
  on_duty: number;
  total: number;
  recommended: number;
}

interface Allocation {
  department: string;
  doctors: number;
  nurses: number;
  technicians: number;
}

interface StaffData {
  doctors: StaffCategory;
  nurses: StaffCategory;
  technicians: StaffCategory;
  allocation: Allocation[];
}

const StaffPanel = () => {
  const [staffData, setStaffData] = useState<StaffData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStaffData = async () => {
      try {
        const response = await api.get('/staff');
        setStaffData(response.data);
        setError(null);
      } catch (err) {
        console.error('Error fetching staff data:', err);
        setError('Failed to load staff data');
      } finally {
        setLoading(false);
      }
    };

    fetchStaffData();
    const interval = setInterval(fetchStaffData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="p-4 text-muted-foreground animate-pulse">Loading staff data...</div>;
  if (error) return <div className="p-4 text-rose-500 bg-rose-500/10 rounded-lg border border-rose-500/20">{error}</div>;
  if (!staffData) return null;

  return (
    <Card className="p-6 backdrop-blur-md bg-white/5 border-white/10 shadow-xl hover:bg-white/10 transition-all duration-300">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-semibold">Department Allocation</h3>
      </div>

      <div className="space-y-3">
        {staffData.allocation.map((dept, index) => {
          const totalStaff = dept.doctors + dept.nurses + dept.technicians;
          const isAdequate = totalStaff >= 30; // Threshold for adequate staffing

          return (
            <div
              key={index}
              className="flex items-center justify-between p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-all duration-200 border border-white/5 group"
            >
              <div className="flex items-center gap-3 flex-1">
                <div className={`w-2 h-2 rounded-full ${isAdequate ? 'bg-emerald-500 shadow-lg shadow-emerald-500/50' : 'bg-amber-500 shadow-lg shadow-amber-500/50'}`} />
                <span className="font-medium text-sm">{dept.department}</span>
              </div>

              <div className="flex items-center gap-4 text-sm text-muted-foreground">
                <span className="flex items-center gap-1">
                  <span className="text-xs opacity-70">Dr:</span>
                  <span className="font-semibold text-white">{dept.doctors}</span>
                </span>
                <span className="flex items-center gap-1">
                  <span className="text-xs opacity-70">Ns:</span>
                  <span className="font-semibold text-white">{dept.nurses}</span>
                </span>
                <span className="flex items-center gap-1">
                  <span className="text-xs opacity-70">Tc:</span>
                  <span className="font-semibold text-white">{dept.technicians}</span>
                </span>
                <Badge
                  variant="outline"
                  className={`ml-2 ${isAdequate
                      ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20'
                      : 'bg-amber-500/10 text-amber-500 border-amber-500/20'
                    }`}
                >
                  {isAdequate ? 'Adequate' : 'Low'}
                </Badge>
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
};

export { StaffPanel };
