import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Activity, CheckCircle, AlertTriangle, Clock, TrendingUp, Zap, Brain } from "lucide-react";
import { useState, useEffect } from "react";

export const ActivityPanel = () => {
  const [activityData, setActivityData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchActivityData = async () => {
      try {
        setError(null);
        const response = await fetch('http://localhost:5000/api/activity');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setActivityData(data);
      } catch (err) {
        console.error('Error fetching activity data:', err);
        setError('Failed to load AI activity data. Please check if the backend is running.');
      } finally {
        setLoading(false);
      }
    };

    fetchActivityData();
    const interval = setInterval(fetchActivityData, 30000); // Refresh every 30 seconds
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

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800 border-green-200';
      case 'processing': return 'bg-blue-100 text-blue-800 border-blue-200';
      default: return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">🤖 AI Agent Activity</h2>
          <p className="text-gray-600">Real-time system intelligence and automated actions</p>
        </div>
        <Badge className="bg-green-100 text-green-800 border-green-200">
          <div className="w-2 h-2 rounded-full bg-green-500 mr-2 animate-pulse"></div>
          System Active
        </Badge>
      </div>

      {/* AI Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-6 bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Model Accuracy</p>
              <p className="text-2xl font-bold text-gray-900">{activityData.model_performance.accuracy}%</p>
              <p className="text-xs text-gray-500">Last updated: {new Date(activityData.model_performance.last_updated).toLocaleDateString()}</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-full">
              <Brain className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </Card>

        <Card className="p-6 bg-gradient-to-br from-green-50 to-emerald-50 border-green-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Predictions Today</p>
              <p className="text-2xl font-bold text-gray-900">{activityData.recent_predictions.length}</p>
              <p className="text-xs text-gray-500">Active predictions</p>
            </div>
            <div className="p-3 bg-green-100 rounded-full">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </Card>

        <Card className="p-6 bg-gradient-to-br from-purple-50 to-violet-50 border-purple-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">System Uptime</p>
              <p className="text-2xl font-bold text-gray-900">{activityData.system_health.uptime}</p>
              <p className="text-xs text-gray-500">Operational</p>
            </div>
            <div className="p-3 bg-purple-100 rounded-full">
              <Activity className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </Card>

        <Card className="p-6 bg-gradient-to-br from-orange-50 to-red-50 border-orange-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Processes</p>
              <p className="text-2xl font-bold text-gray-900">{activityData.active_processes.length}</p>
              <p className="text-xs text-gray-500">Running tasks</p>
            </div>
            <div className="p-3 bg-orange-100 rounded-full">
              <Zap className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </Card>
      </div>

      {/* Recent Predictions */}
      <Card className="shadow-lg overflow-hidden">
        <div className="px-6 py-4 bg-gray-50 border-b">
          <h3 className="text-lg font-semibold text-gray-900">Recent AI Predictions</h3>
        </div>
        <div className="divide-y divide-gray-200">
          {activityData.recent_predictions.map((prediction, index) => (
            <div key={index} className="p-6 hover:bg-gray-50 transition-colors">
              <div className="flex items-start gap-4">
                <div className={`p-3 rounded-full ${getStatusColor(prediction.status)}`}>
                  {prediction.status === 'completed' ? <CheckCircle size={20} /> : <Clock size={20} />}
                </div>

                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-lg font-semibold text-gray-900">{prediction.type}</h4>
                    <Badge variant="outline" className={getStatusColor(prediction.status)}>
                      {prediction.status}
                    </Badge>
                  </div>

                  <p className="text-gray-700 mb-3">{prediction.result}</p>

                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <span>Confidence: {prediction.confidence}</span>
                    <span>{new Date(prediction.timestamp).toLocaleString()}</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Active Processes */}
      <Card className="p-6 bg-gradient-to-br from-indigo-50 to-blue-50 border-indigo-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">⚙️ Active Processes</h3>
        <div className="space-y-4">
          {activityData.active_processes.map((process, index) => (
            <div key={index} className="flex items-center justify-between p-4 bg-white rounded-lg border border-indigo-100">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-indigo-100 rounded-full">
                  <Activity className="w-4 h-4 text-indigo-600" />
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">{process.name}</h4>
                  <p className="text-sm text-gray-600">Status: {process.status}</p>
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm font-medium text-gray-900">{process.progress}%</div>
                <div className="w-20 bg-gray-200 rounded-full h-2 mt-1">
                  <div
                    className="bg-indigo-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${process.progress}%` }}
                  ></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* System Health */}
      <Card className="p-6 bg-gradient-to-br from-green-50 to-emerald-50 border-green-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">🩺 System Health</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium ${
              activityData.system_health.status === 'healthy'
                ? 'bg-green-100 text-green-800'
                : 'bg-red-100 text-red-800'
            }`}>
              <div className={`w-2 h-2 rounded-full ${
                activityData.system_health.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'
              } animate-pulse`}></div>
              {activityData.system_health.status}
            </div>
            <p className="text-xs text-gray-600 mt-2">Overall Status</p>
          </div>

          <div className="text-center">
            <p className="text-lg font-semibold text-gray-900">{activityData.system_health.uptime}</p>
            <p className="text-xs text-gray-600">Uptime</p>
          </div>

          <div className="text-center">
            <p className="text-lg font-semibold text-gray-900">
              {new Date(activityData.system_health.last_backup).toLocaleString()}
            </p>
            <p className="text-xs text-gray-600">Last Backup</p>
          </div>
        </div>
      </Card>

      <div className="text-center">
        <p className="text-xs text-gray-500">
          Data refreshes every 30 seconds • AI-powered monitoring system
        </p>
      </div>
    </div>
  );
};
