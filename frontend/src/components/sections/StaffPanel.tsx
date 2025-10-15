import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { UserCheck, AlertTriangle, CheckCircle, Clock } from "lucide-react";
import { useState, useEffect } from "react";
import { getStaffRecommendationsHistory } from "@/services/supabase";

interface StaffData {
  department: string;
  current: number;
  required: number;
  recommendation: string;
  status: "adequate" | "shortage" | "excess";
}

const StaffPanel = () => {
  const [staffData, setStaffData] = useState<StaffData[]>([]);
  const [shifts, setShifts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStaffData = async () => {
      try {
        const response = await fetch('/api/resource-status');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();

        // Transform backend data to match frontend interface
        const transformedStaffData: StaffData[] = [
          {
            department: "Emergency",
            current: Math.floor(data.staff.doctors_on_duty * 0.4),
            required: Math.floor(data.staff.doctors_on_duty * 0.45),
            recommendation: `Need ${Math.max(0, Math.floor(data.staff.doctors_on_duty * 0.45) - Math.floor(data.staff.doctors_on_duty * 0.4))} more doctors`,
            status: Math.floor(data.staff.doctors_on_duty * 0.4) >= Math.floor(data.staff.doctors_on_duty * 0.45) ? "adequate" : "shortage",
          },
          {
            department: "ICU",
            current: Math.floor(data.staff.nurses_on_duty * 0.3),
            required: Math.floor(data.staff.nurses_on_duty * 0.35),
            recommendation: `Need ${Math.max(0, Math.floor(data.staff.nurses_on_duty * 0.35) - Math.floor(data.staff.nurses_on_duty * 0.3))} more nurses`,
            status: Math.floor(data.staff.nurses_on_duty * 0.3) >= Math.floor(data.staff.nurses_on_duty * 0.35) ? "adequate" : "shortage",
          },
          {
            department: "General Ward",
            current: Math.floor(data.staff.nurses_on_duty * 0.4),
            required: Math.floor(data.staff.nurses_on_duty * 0.42),
            recommendation: `Need ${Math.max(0, Math.floor(data.staff.nurses_on_duty * 0.42) - Math.floor(data.staff.nurses_on_duty * 0.4))} more nurses`,
            status: Math.floor(data.staff.nurses_on_duty * 0.4) >= Math.floor(data.staff.nurses_on_duty * 0.42) ? "adequate" : "shortage",
          },
        ];

        setStaffData(transformedStaffData);

        // Calculate shift data from resource status
        const totalStaff = data.staff.doctors_on_duty + data.staff.nurses_on_duty;
        setShifts([
          { shift: "Morning (6 AM - 2 PM)", staff: Math.floor(totalStaff * 0.4), utilization: Math.floor(data.staff.shift_coverage * 100) },
          { shift: "Evening (2 PM - 10 PM)", staff: Math.floor(totalStaff * 0.35), utilization: Math.floor(data.staff.shift_coverage * 100) - 5 },
          { shift: "Night (10 PM - 6 AM)", staff: Math.floor(totalStaff * 0.25), utilization: Math.floor(data.staff.shift_coverage * 100) - 15 },
        ]);

      } catch (error) {
        console.error('Error fetching staff data:', error);
        // Set fallback data on error
        setStaffData([
          {
            department: "Emergency",
            current: 18,
            required: 20,
            recommendation: "Need 2 more doctors",
            status: "shortage",
          },
          {
            department: "ICU",
            current: 36,
            required: 42,
            recommendation: "Need 6 more nurses",
            status: "shortage",
          },
          {
            department: "General Ward",
            current: 48,
            required: 50,
            recommendation: "Need 2 more nurses",
            status: "adequate",
          },
        ]);
        setShifts([
          { shift: "Morning (6 AM - 2 PM)", staff: 58, utilization: 92 },
          { shift: "Evening (2 PM - 10 PM)", staff: 51, utilization: 88 },
          { shift: "Night (10 PM - 6 AM)", staff: 37, utilization: 76 },
        ]);
      } finally {
        setLoading(false);
      }
    };

    // Initial fetch
    fetchStaffData();

    // Set up real-time polling every 5 seconds
    const interval = setInterval(fetchStaffData, 5000);

    // Cleanup interval on component unmount
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <div className="flex justify-center items-center h-64">Loading staff data...</div>;
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Staff Allocation</h2>
          <p className="text-muted-foreground">AI-optimized staffing recommendations</p>
        </div>
        <Button className="bg-gradient-primary shadow-medium hover:shadow-strong">
          <UserCheck size={18} className="mr-2" />
          Apply AI Recommendations
        </Button>
      </div>

      {/* Department Staffing Table */}
      <Card className="shadow-soft overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-secondary">
              <tr>
                <th className="text-left p-4 text-sm font-semibold text-secondary-foreground">Department</th>
                <th className="text-center p-4 text-sm font-semibold text-secondary-foreground">Current Staff</th>
                <th className="text-center p-4 text-sm font-semibold text-secondary-foreground">Required</th>
                <th className="text-center p-4 text-sm font-semibold text-secondary-foreground">Status</th>
                <th className="text-left p-4 text-sm font-semibold text-secondary-foreground">AI Recommendation</th>
                <th className="text-center p-4 text-sm font-semibold text-secondary-foreground">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {staffData.map((dept) => {
                const Icon =
                  dept.status === 'shortage' ? AlertTriangle :
                  dept.status === 'excess' ? Clock : CheckCircle;

                const statusConfig = {
                  adequate: { bg: "bg-success/10", text: "text-success", label: "Adequate" },
                  shortage: { bg: "bg-destructive/10", text: "text-destructive", label: "Shortage" },
                  excess: { bg: "bg-accent/10", text: "text-accent", label: "Excess" },
                };

                return (
                  <tr key={dept.department} className="hover:bg-muted/50 transition-colors">
                    <td className="p-4">
                      <span className="font-medium text-foreground">{dept.department}</span>
                    </td>
                    <td className="p-4 text-center">
                      <span className="text-foreground font-semibold">{dept.current}</span>
                    </td>
                    <td className="p-4 text-center">
                      <span className="text-muted-foreground">{dept.required}</span>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center justify-center gap-2">
                        <Badge variant="outline" className={`${statusConfig[dept.status].bg} ${statusConfig[dept.status].text} border-0`}>
                          <Icon size={12} className="mr-1" />
                          {statusConfig[dept.status].label}
                        </Badge>
                      </div>
                    </td>
                    <td className="p-4">
                      <span className="text-sm text-muted-foreground">{dept.recommendation}</span>
                    </td>
                    <td className="p-4 text-center">
                      <Button variant="outline" size="sm" className="text-primary border-primary hover:bg-primary hover:text-primary-foreground">
                        Adjust
                      </Button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Shift Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {shifts.map((shift) => (
          <Card key={shift.shift} className="p-5 shadow-soft">
            <h4 className="font-semibold text-foreground mb-3">{shift.shift}</h4>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-muted-foreground">Assigned Staff</p>
                <p className="text-2xl font-bold text-foreground">{shift.staff}</p>
              </div>
              <div>
                <div className="flex items-center justify-between mb-1">
                  <p className="text-sm text-muted-foreground">Utilization</p>
                  <p className="text-sm font-medium text-foreground">{shift.utilization}%</p>
                </div>
                <div className="h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${
                      shift.utilization > 90 ? 'bg-destructive' :
                      shift.utilization > 80 ? 'bg-warning' : 'bg-success'
                    }`}
                    style={{ width: `${shift.utilization}%` }}
                  />
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};

export { StaffPanel };
