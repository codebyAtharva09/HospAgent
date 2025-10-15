import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Activity, CheckCircle, AlertTriangle, Clock, TrendingUp } from "lucide-react";

interface AgentLog {
  id: string;
  timestamp: string;
  action: string;
  status: "completed" | "processing" | "warning";
  details: string;
  impact?: string;
}

const agentLogs: AgentLog[] = [
  {
    id: "1",
    timestamp: "10 min ago",
    action: "Patient Surge Prediction",
    status: "completed",
    details: "Analyzed 48-hour historical data and weather patterns",
    impact: "Generated alert for 35% patient increase",
  },
  {
    id: "2",
    timestamp: "15 min ago",
    action: "Staff Reallocation",
    status: "completed",
    details: "Optimized staff distribution across departments",
    impact: "Recommended 6 nurses move to Emergency",
  },
  {
    id: "3",
    timestamp: "22 min ago",
    action: "Inventory Forecast",
    status: "warning",
    details: "Detected critical supply levels for N95 masks",
    impact: "Auto-generated reorder request",
  },
  {
    id: "4",
    timestamp: "28 min ago",
    action: "Patient Advisory Generation",
    status: "completed",
    details: "Created public advisory for Emergency wait times",
    impact: "Ready for review and publication",
  },
  {
    id: "5",
    timestamp: "35 min ago",
    action: "ICU Capacity Analysis",
    status: "processing",
    details: "Evaluating ICU bed requirements for next 12 hours",
    impact: "Prediction in progress...",
  },
  {
    id: "6",
    timestamp: "42 min ago",
    action: "Area Health Mapping",
    status: "completed",
    details: "Updated health risk heatmap for all zones",
    impact: "Identified 2 high-risk zones",
  },
];

const agentStats = [
  { label: "Actions Today", value: 247, icon: Activity, trend: "+12%" },
  { label: "Accuracy Rate", value: "94.2%", icon: CheckCircle, trend: "+2.1%" },
  { label: "Predictions Made", value: 64, icon: TrendingUp, trend: "+8%" },
  { label: "Avg Response", value: "2.3s", icon: Clock, trend: "-0.4s" },
];

export const ActivityPanel = () => {
  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h2 className="text-2xl font-bold text-foreground">AI Agent Activity</h2>
        <p className="text-muted-foreground">Real-time system intelligence and actions</p>
      </div>

      {/* Agent Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {agentStats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.label} className="p-5 shadow-soft bg-gradient-card">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-muted-foreground font-medium">{stat.label}</p>
                  <h3 className="text-2xl font-bold text-foreground mt-1">{stat.value}</h3>
                  <p className="text-xs text-success font-medium mt-2">{stat.trend}</p>
                </div>
                <div className="p-3 rounded-xl bg-primary/10">
                  <Icon className="text-primary" size={20} />
                </div>
              </div>
            </Card>
          );
        })}
      </div>

      {/* Activity Log */}
      <Card className="shadow-soft">
        <div className="p-6 border-b border-border">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-foreground">Recent Agent Actions</h3>
            <Badge variant="outline" className="bg-success/10 text-success border-success">
              <div className="w-2 h-2 rounded-full bg-success mr-2 animate-pulse-soft" />
              Active
            </Badge>
          </div>
        </div>

        <div className="divide-y divide-border">
          {agentLogs.map((log) => {
            const statusConfig = {
              completed: {
                icon: CheckCircle,
                bg: "bg-success/10",
                text: "text-success",
                border: "border-success/20",
                label: "Completed",
              },
              processing: {
                icon: Clock,
                bg: "bg-accent/10",
                text: "text-accent",
                border: "border-accent/20",
                label: "Processing",
              },
              warning: {
                icon: AlertTriangle,
                bg: "bg-warning/10",
                text: "text-warning",
                border: "border-warning/20",
                label: "Warning",
              },
            };

            const config = statusConfig[log.status];
            const Icon = config.icon;

            return (
              <div key={log.id} className="p-5 hover:bg-muted/30 transition-colors">
                <div className="flex items-start gap-4">
                  <div className={`p-2.5 rounded-lg ${config.bg} flex-shrink-0`}>
                    <Icon className={config.text} size={20} />
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-3 mb-1">
                      <h4 className="font-semibold text-foreground">{log.action}</h4>
                      <span className="text-xs text-muted-foreground whitespace-nowrap">
                        {log.timestamp}
                      </span>
                    </div>

                    <p className="text-sm text-muted-foreground mb-2">{log.details}</p>

                    {log.impact && (
                      <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-md border ${config.border} ${config.bg}`}>
                        <span className="text-xs font-medium text-foreground">
                          Impact: {log.impact}
                        </span>
                      </div>
                    )}
                  </div>

                  <Badge variant="outline" className={`${config.bg} ${config.text} border-0 flex-shrink-0`}>
                    {config.label}
                  </Badge>
                </div>
              </div>
            );
          })}
        </div>
      </Card>

      {/* System Health */}
      <Card className="p-6 shadow-soft">
        <h3 className="text-lg font-semibold text-foreground mb-4">System Health</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <p className="text-sm text-muted-foreground">Model Status</p>
            <div className="flex items-center gap-2 mt-2">
              <div className="w-3 h-3 rounded-full bg-success animate-pulse-soft" />
              <p className="text-lg font-semibold text-success">Operational</p>
            </div>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Data Freshness</p>
            <p className="text-lg font-semibold text-foreground mt-2">Live (5s delay)</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Last Model Update</p>
            <p className="text-lg font-semibold text-foreground mt-2">2 hours ago</p>
          </div>
        </div>
      </Card>
    </div>
  );
};
