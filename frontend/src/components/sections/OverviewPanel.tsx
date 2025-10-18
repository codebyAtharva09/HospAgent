import { Card } from "@/components/ui/card";
import { AlertTriangle, Bed, Users, Activity } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { useEffect, useState } from "react";
import axios from "axios";

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: string;
  icon: React.ElementType;
  status?: "stable" | "warning" | "critical";
}

const MetricCard = ({ title, value, change, icon: Icon, status = "stable" }: MetricCardProps) => {
  const statusColors = {
    stable: "text-success",
    warning: "text-warning",
    critical: "text-destructive",
  };

  return (
    <Card className="p-6 bg-gradient-card shadow-soft hover:shadow-medium transition-shadow">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-muted-foreground font-medium">{title}</p>
          <h3 className="text-3xl font-bold text-foreground mt-2">{value}</h3>
          {change && (
            <p className={`text-sm mt-2 font-medium ${statusColors[status]}`}>
              {change}
            </p>
          )}
        </div>
        <div className={`p-3 rounded-xl ${status === 'critical' ? 'bg-destructive/10' : status === 'warning' ? 'bg-warning/10' : 'bg-success/10'}`}>
          <Icon className={statusColors[status]} size={24} />
        </div>
      </div>
    </Card>
  );
};

interface DashboardData {
  total_patients: number;
  available_beds: number;
  icu_occupancy: string;
  staff_on_duty: number;
  department_status: Record<string, number>;
  latest_prediction?: any;
  latest_recommendation?: any;
  latest_advisory?: any;
  last_updated: string;
  error?: string;
}

export const OverviewPanel = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const response = await axios.get('http://localhost:5000/api/dashboard');
        setData(response.data);
        setError(null);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data');
        // Fallback to static data
        setData({
          total_patients: 487,
          available_beds: 63,
          icu_occupancy: "89%",
          staff_on_duty: 142,
          department_status: {
            "Emergency": 85,
            "General Ward": 67,
            "ICU": 92,
            "Pediatrics": 54,
            "Surgery": 71,
          },
          last_updated: new Date().toISOString()
        });
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();

    // Refresh data every 30 seconds
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Hospital Overview</h2>
          <p className="text-muted-foreground">Loading dashboard data...</p>
        </div>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h2 className="text-2xl font-bold text-foreground">Hospital Overview</h2>
        <p className="text-muted-foreground">
          Real-time hospital status and alerts
          {data.last_updated && (
            <span className="text-xs ml-2">
              (Last updated: {new Date(data.last_updated).toLocaleTimeString()})
            </span>
          )}
        </p>
      </div>

      {/* Error Banner */}
      {error && (
        <Card className="p-4 border-l-4 border-l-destructive bg-destructive/5">
          <div className="flex items-start gap-3">
            <AlertTriangle className="text-destructive flex-shrink-0 mt-0.5" size={20} />
            <div className="flex-1">
              <h4 className="font-semibold text-foreground">Connection Error</h4>
              <p className="text-sm text-muted-foreground mt-1">
                {error}. Showing cached data.
              </p>
            </div>
          </div>
        </Card>
      )}

      {/* Alert Banner */}
      <Card className="p-4 border-l-4 border-l-warning bg-warning/5">
        <div className="flex items-start gap-3">
          <AlertTriangle className="text-warning flex-shrink-0 mt-0.5" size={20} />
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <h4 className="font-semibold text-foreground">Predicted Patient Surge</h4>
              <Badge variant="outline" className="bg-warning/10 text-warning border-warning">
                Next 6 hours
              </Badge>
            </div>
            <p className="text-sm text-muted-foreground mt-1">
              AI forecasts 35% increase in emergency admissions. Recommend activating overflow protocols.
            </p>
          </div>
        </div>
      </Card>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Patients"
          value={data.total_patients}
          change="+12% from yesterday"
          icon={Users}
          status="warning"
        />
        <MetricCard
          title="Available Beds"
          value={data.available_beds}
          change={`${Math.round((data.available_beds / 500) * 100)}% capacity`}
          icon={Bed}
          status="stable"
        />
        <MetricCard
          title="ICU Occupancy"
          value={data.icu_occupancy}
          change="Critical threshold"
          icon={Activity}
          status="critical"
        />
        <MetricCard
          title="Staff on Duty"
          value={data.staff_on_duty}
          change="Full roster"
          icon={Users}
          status="stable"
        />
      </div>

      {/* Department Status */}
      <Card className="p-6 shadow-soft">
        <h3 className="text-lg font-semibold text-foreground mb-4">Department Status</h3>
        <div className="space-y-3">
          {Object.entries(data.department_status).map(([dept, load]) => {
            let status: "stable" | "warning" | "critical" = "stable";
            if (load >= 85) status = "critical";
            else if (load >= 65) status = "warning";

            return (
              <div key={dept} className="flex items-center gap-4">
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-foreground">{dept}</span>
                    <span className="text-sm text-muted-foreground">{load}%</span>
                  </div>
                  <div className="h-2 bg-muted rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all ${
                        status === 'critical' ? 'bg-red-500' :
                        status === 'warning' ? 'bg-yellow-500' : 'bg-green-500'
                      }`}
                      style={{ width: `${load}%` }}
                    />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </Card>
    </div>
  );
};
