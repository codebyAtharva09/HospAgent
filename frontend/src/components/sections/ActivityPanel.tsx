import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Activity, Brain, Zap, CheckCircle, Clock, Server } from "lucide-react";
import api from "@/services/api";

interface Prediction {
  type: string;
  result: string;
  confidence: string;
  timestamp: string;
  status: 'completed' | 'processing' | 'pending';
}

interface Process {
  name: string;
  status: string;
  progress: number;
}

interface SystemHealth {
  status: 'healthy' | 'degraded' | 'critical';
  uptime: string;
  last_backup: string;
}

interface ActivityData {
  recent_predictions: Prediction[];
  active_processes: Process[];
  system_health: SystemHealth;
  model_performance: {
    accuracy: number;
    last_updated: string;
  };
}

const ActivityPanel = () => {
  const [activityData, setActivityData] = useState<ActivityData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchActivityData = async () => {
      try {
        const response = await api.get('/activity');
        setActivityData(response.data);
        setError(null);
      } catch (err) {
        console.error('Error fetching activity data:', err);
        setError('Failed to load activity data');
      } finally {
        setLoading(false);
      }
    };

    fetchActivityData();
    const interval = setInterval(fetchActivityData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="p-4 text-muted-foreground animate-pulse">Loading activity...</div>;
  if (error) return <div className="p-4 text-rose-500 bg-rose-500/10 rounded-lg border border-rose-500/20">{error}</div>;
  if (!activityData) return null;

  return (
    <div className="space-y-6 h-full flex flex-col">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold flex items-center gap-2">
          <Activity className="h-5 w-5 text-cyan-500" />
          System Activity
        </h2>
        <div className="flex items-center gap-2">
          <div className={`h-2 w-2 rounded-full animate-pulse ${activityData.system_health.status === 'healthy' ? 'bg-emerald-500' : 'bg-rose-500'
            }`} />
          <span className="text-sm text-muted-foreground capitalize">{activityData.system_health.status}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Stats */}
        <div className="lg:col-span-2 space-y-6">
          {/* Recent Predictions */}
          <Card className="p-0 backdrop-blur-md bg-white/5 border-white/10 shadow-lg overflow-hidden">
            <div className="p-4 border-b border-white/10 flex justify-between items-center">
              <h3 className="font-medium flex items-center gap-2">
                <Brain className="h-4 w-4 text-purple-500" />
                Recent AI Predictions
              </h3>
              <Badge variant="outline" className="bg-purple-500/10 text-purple-500 border-purple-500/20">
                {activityData.model_performance.accuracy}% Accuracy
              </Badge>
            </div>
            <div className="divide-y divide-white/5">
              {activityData.recent_predictions.map((pred, index) => (
                <div key={index} className="p-4 hover:bg-white/5 transition-colors">
                  <div className="flex justify-between items-start mb-1">
                    <h4 className="font-medium text-sm">{pred.type}</h4>
                    <Badge variant="secondary" className="text-xs">
                      {pred.confidence}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground mb-2">{pred.result}</p>
                  <div className="flex items-center gap-2 text-xs text-muted-foreground/60">
                    <Clock className="h-3 w-3" />
                    {new Date(pred.timestamp).toLocaleTimeString()}
                    <span className="mx-1">•</span>
                    <span className={pred.status === 'completed' ? 'text-emerald-500' : 'text-amber-500'}>
                      {pred.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* Sidebar Stats */}
        <div className="space-y-6">
          {/* Active Processes */}
          <Card className="p-4 backdrop-blur-md bg-white/5 border-white/10 shadow-lg">
            <h3 className="font-medium mb-4 flex items-center gap-2">
              <Zap className="h-4 w-4 text-amber-500" />
              Active Processes
            </h3>
            <div className="space-y-4">
              {activityData.active_processes.map((process, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>{process.name}</span>
                    <span className="text-muted-foreground">{process.progress}%</span>
                  </div>
                  <div className="h-1.5 w-full bg-white/10 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-amber-500 rounded-full transition-all duration-500"
                      style={{ width: `${process.progress}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </Card>

          {/* System Info */}
          <Card className="p-4 backdrop-blur-md bg-white/5 border-white/10 shadow-lg">
            <h3 className="font-medium mb-4 flex items-center gap-2">
              <Server className="h-4 w-4 text-cyan-500" />
              System Info
            </h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between py-2 border-b border-white/5">
                <span className="text-muted-foreground">Uptime</span>
                <span className="font-mono">{activityData.system_health.uptime}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-white/5">
                <span className="text-muted-foreground">Last Backup</span>
                <span>{new Date(activityData.system_health.last_backup).toLocaleDateString()}</span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-muted-foreground">Model Update</span>
                <span>{new Date(activityData.model_performance.last_updated).toLocaleDateString()}</span>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export { ActivityPanel };
