import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { AlertCircle, Bell, Info, CheckCircle, Share2, FileText } from "lucide-react";
import api from "@/services/api";

interface Alert {
  id: string;
  title: string;
  message: string;
  priority: 'high' | 'medium' | 'low';
  timestamp: string;
  target_audience: string;
}

interface Recommendation {
  category: string;
  advice: string;
  validity: string;
}

interface AdvisoryData {
  current_alerts: Alert[];
  recommendations: Recommendation[];
  communication_channels: string[];
}

const AdvisoryPanel = () => {
  const [advisoryData, setAdvisoryData] = useState<AdvisoryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAdvisoryData = async () => {
      try {
        const response = await api.get('/advisory');
        setAdvisoryData(response.data);
        setError(null);
      } catch (err) {
        console.error('Error fetching advisory data:', err);
        setError('Failed to load advisory data');
      } finally {
        setLoading(false);
      }
    };

    fetchAdvisoryData();
    const interval = setInterval(fetchAdvisoryData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="p-4 text-muted-foreground animate-pulse">Loading advisories...</div>;
  if (error) return <div className="p-4 text-rose-500 bg-rose-500/10 rounded-lg border border-rose-500/20">{error}</div>;
  if (!advisoryData) return null;

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-rose-500/10 text-rose-500 border-rose-500/20';
      case 'medium': return 'bg-amber-500/10 text-amber-500 border-amber-500/20';
      case 'low': return 'bg-blue-500/10 text-blue-500 border-blue-500/20';
      default: return 'bg-slate-500/10 text-slate-500 border-slate-500/20';
    }
  };

  return (
    <div className="space-y-6 h-full flex flex-col">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold flex items-center gap-2">
          <Bell className="h-5 w-5 text-amber-500" />
          Advisories & Alerts
        </h2>
        <Badge variant="outline" className="bg-amber-500/10 text-amber-500 border-amber-500/20">
          {advisoryData.current_alerts.length} Active
        </Badge>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Active Alerts */}
        <div className="space-y-4">
          <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Current Alerts</h3>
          {advisoryData.current_alerts.map((alert, index) => (
            <Card key={index} className="p-4 backdrop-blur-md bg-white/5 border-white/10 shadow-lg hover:bg-white/10 transition-colors">
              <div className="flex justify-between items-start mb-2">
                <div className="flex items-center gap-2">
                  <AlertCircle className={`h-5 w-5 ${alert.priority === 'high' ? 'text-rose-500' :
                      alert.priority === 'medium' ? 'text-amber-500' : 'text-blue-500'
                    }`} />
                  <h4 className="font-semibold">{alert.title}</h4>
                </div>
                <Badge variant="outline" className={getPriorityColor(alert.priority)}>
                  {alert.priority}
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground mb-3">{alert.message}</p>
              <div className="flex justify-between items-center text-xs text-muted-foreground border-t border-white/5 pt-3">
                <span>Target: {alert.target_audience}</span>
                <span>{new Date(alert.timestamp).toLocaleTimeString()}</span>
              </div>
              <div className="mt-3 flex gap-2">
                <Button size="sm" variant="ghost" className="h-8 px-2 text-xs hover:bg-white/10">
                  <Share2 className="h-3 w-3 mr-1" /> Share
                </Button>
                <Button size="sm" variant="ghost" className="h-8 px-2 text-xs hover:bg-white/10">
                  <FileText className="h-3 w-3 mr-1" /> Details
                </Button>
              </div>
            </Card>
          ))}
        </div>

        {/* Recommendations */}
        <div className="space-y-4">
          <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">AI Recommendations</h3>
          {advisoryData.recommendations.map((rec, index) => (
            <Card key={index} className="p-4 backdrop-blur-md bg-white/5 border-white/10 shadow-lg">
              <div className="flex items-start gap-3">
                <div className="p-2 rounded-full bg-indigo-500/10 text-indigo-500">
                  <Info className="h-5 w-5" />
                </div>
                <div>
                  <h4 className="font-medium text-indigo-400 mb-1">{rec.category}</h4>
                  <p className="text-sm text-muted-foreground">{rec.advice}</p>
                  <p className="text-xs text-muted-foreground/60 mt-2">Valid until: {rec.validity}</p>
                </div>
              </div>
            </Card>
          ))}

          {/* Communication Channels */}
          <div className="mt-6">
            <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-3">Active Channels</h3>
            <div className="flex flex-wrap gap-2">
              {advisoryData.communication_channels.map((channel, index) => (
                <Badge key={index} variant="secondary" className="bg-white/10 hover:bg-white/20 text-foreground">
                  {channel}
                </Badge>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export { AdvisoryPanel };
