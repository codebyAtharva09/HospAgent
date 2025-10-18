import { Card } from "@/components/ui/card";
import { AlertTriangle, Bed, Users, Activity, TrendingUp, Clock } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { useEffect, useState } from "react";

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: string;
  icon: React.ElementType;
  status?: "stable" | "warning" | "critical";
}

const MetricCard = ({ title, value, change, icon: Icon, status = "stable" }: MetricCardProps) => {
  const statusColors = {
    stable: "text-green-600",
    warning: "text-yellow-600",
    critical: "text-red-600",
  };

  const bgColors = {
    stable: "bg-green-50 border-green-200",
    warning: "bg-yellow-50 border-yellow-200",
    critical: "bg-red-50 border-red-200",
  };

  return (
    <Card className={`p-6 ${bgColors[status]} shadow-lg hover:shadow-xl transition-shadow border`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-gray-600 font-medium">{title}</p>
          <h3 className="text-3xl font-bold text-gray-900 mt-2">{value}</h3>
          {change && (
            <p className={`text-sm mt-2 font-medium ${statusColors[status]}`}>
              {change}
            </p>
          )}
        </div>
        <div className={`p-3 rounded-xl ${status === 'critical' ? 'bg-red-100' : status === 'warning' ? 'bg-yellow-100' : 'bg-green-100'}`}>
          <Icon className={statusColors[status]} size={24} />
        </div>
      </div>
    </Card>
  );
};

export const OverviewPanel = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchOverviewData = async () => {
      try {
        setError(null);
        const response = await fetch('http://localhost:5000/api/overview');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const overviewData = await response.json();
        setData(overviewData);
      } catch (err) {
        console.error('Error fetching overview data:', err);
        setError('Failed to load overview data. Please check if the backend is running.');
      } finally {
        setLoading(false);
      }
    };

    fetchOverviewData();
    const interval = setInterval(fetchOverviewData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="p-6 bg-white rounded-2xl shadow-lg">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-20 bg-gray-200 rounded"></div>
            ))}
          </div>
          <div className="h-64 bg-gray-200 rounded"></div>
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
          <h2 className="text-2xl font-bold text-gray-900">🏥 Hospital Overview</h2>
          <p className="text-gray-600">
            Real-time hospital status and AI-powered insights
            {data.last_updated && (
              <span className="text-xs ml-2 text-gray-500">
                (Last updated: {new Date(data.last_updated).toLocaleTimeString()})
              </span>
            )}
          </p>
        </div>
        <Badge className="bg-blue-100 text-blue-800 border-blue-200">
          <Clock size={12} className="mr-1" />
          Live Data
        </Badge>
      </div>

      {/* Alert Banner */}
      <Card className="p-4 border-l-4 border-l-yellow-500 bg-yellow-50">
        <div className="flex items-start gap-3">
          <AlertTriangle className="text-yellow-600 flex-shrink-0 mt-0.5" size={20} />
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <h4 className="font-semibold text-gray-900">AI Prediction Alert</h4>
              <Badge variant="outline" className="bg-yellow-100 text-yellow-800 border-yellow-200">
                Next 24 hours
              </Badge>
            </div>
            <p className="text-sm text-gray-700 mt-1">
              AI forecasts potential patient surge. Monitor capacity and prepare contingency plans.
            </p>
          </div>
        </div>
      </Card>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Patients"
          value={data.patient_stats.current_patients}
          change={`+${data.patient_stats.admitted_today} admitted today`}
          icon={Users}
          status="warning"
        />
        <MetricCard
          title="Available Beds"
          value={data.hospital_status.available_beds}
          change={`${Math.round((data.hospital_status.available_beds / data.hospital_status.total_beds) * 100)}% available`}
          icon={Bed}
          status={data.hospital_status.available_beds < 50 ? "critical" : "stable"}
        />
        <MetricCard
          title="Bed Utilization"
          value={`${Math.round(data.hospital_status.utilization_rate * 100)}%`}
          change="Current occupancy"
          icon={Activity}
          status={data.hospital_status.utilization_rate > 0.9 ? "critical" : data.hospital_status.utilization_rate > 0.8 ? "warning" : "stable"}
        />
        <MetricCard
          title="Alerts Active"
          value={data.alerts_count}
          change="Require attention"
          icon={AlertTriangle}
          status={data.alerts_count > 0 ? "warning" : "stable"}
        />
      </div>

      {/* Department Status */}
      <Card className="shadow-lg overflow-hidden">
        <div className="px-6 py-4 bg-gray-50 border-b">
          <h3 className="text-lg font-semibold text-gray-900">Department Status</h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {data.department_status.map((dept, index) => {
              const utilizationPercent = Math.round((dept.patients / (dept.capacity || 100)) * 100);
              let status = "stable";
              if (dept.status === "high") status = "critical";
              else if (utilizationPercent > 80) status = "warning";

              return (
                <div key={index} className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-900">{dept.name}</span>
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-600">{dept.patients}/{dept.capacity || 100}</span>
                      <Badge variant="outline" className={
                        status === 'critical' ? 'bg-red-100 text-red-800 border-red-200' :
                        status === 'warning' ? 'bg-yellow-100 text-yellow-800 border-yellow-200' :
                        'bg-green-100 text-green-800 border-green-200'
                      }>
                        {dept.status}
                      </Badge>
                    </div>
                  </div>
                  <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all ${
                        status === 'critical' ? 'bg-red-500' :
                        status === 'warning' ? 'bg-yellow-500' : 'bg-green-500'
                      }`}
                      style={{ width: `${utilizationPercent}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </Card>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-4 text-center bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200">
          <p className="text-2xl font-bold text-blue-600">
            {data.patient_stats.admitted_today}
          </p>
          <p className="text-sm text-gray-700">Admitted Today</p>
        </Card>

        <Card className="p-4 text-center bg-gradient-to-br from-green-50 to-emerald-50 border-green-200">
          <p className="text-2xl font-bold text-green-600">
            {data.patient_stats.discharged_today}
          </p>
          <p className="text-sm text-gray-700">Discharged Today</p>
        </Card>

        <Card className="p-4 text-center bg-gradient-to-br from-purple-50 to-violet-50 border-purple-200">
          <p className="text-2xl font-bold text-purple-600">
            {data.patient_stats.average_stay}
          </p>
          <p className="text-sm text-gray-700">Avg. Stay (days)</p>
        </Card>
      </div>

      <div className="text-center">
        <p className="text-xs text-gray-500">
          Data refreshes every 30 seconds • AI-powered hospital monitoring
        </p>
      </div>
    </div>
  );
};
