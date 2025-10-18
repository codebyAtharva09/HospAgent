import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Share2, FileText, MapPin, AlertCircle, MessageSquare } from "lucide-react";
import { useState, useEffect } from "react";

export const AdvisoryPanel = () => {
  const [advisoryData, setAdvisoryData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAdvisoryData = async () => {
      try {
        setError(null);
        const response = await fetch('http://localhost:5000/api/advisory');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setAdvisoryData(data);
      } catch (err) {
        console.error('Error fetching advisory data:', err);
        setError('Failed to load advisory data. Please check if the backend is running.');
      } finally {
        setLoading(false);
      }
    };

    fetchAdvisoryData();
    const interval = setInterval(fetchAdvisoryData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="p-6 bg-white rounded-2xl shadow-lg">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
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

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800 border-red-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default: return 'bg-green-100 text-green-800 border-green-200';
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">📢 Patient Advisory</h2>
          <p className="text-gray-600">AI-powered public communication and health alerts</p>
        </div>
        <Button className="bg-blue-500 hover:bg-blue-600 text-white shadow-md">
          <MessageSquare size={18} className="mr-2" />
          Create Advisory
        </Button>
      </div>

      {/* Current Alerts */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">🚨 Current Alerts</h3>
        {advisoryData.current_alerts.map((alert, index) => (
          <Card key={index} className="p-6 bg-gradient-to-br from-white to-red-50 border-red-200 hover:shadow-lg transition-shadow">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-3">
                  <h4 className="text-xl font-semibold text-gray-900">{alert.title}</h4>
                  <Badge variant="outline" className={getPriorityColor(alert.priority)}>
                    {alert.priority.toUpperCase()} PRIORITY
                  </Badge>
                </div>

                <p className="text-gray-700 mb-4 leading-relaxed">{alert.message}</p>

                <div className="flex items-center gap-4 text-sm text-gray-600">
                  <div className="flex items-center gap-1">
                    <MapPin size={14} />
                    <span>Target: {alert.target_audience}</span>
                  </div>
                  <div>
                    {new Date(alert.timestamp).toLocaleString()}
                  </div>
                </div>
              </div>

              <div className="flex flex-col gap-2">
                <Button size="sm" className="bg-blue-500 hover:bg-blue-600 text-white">
                  <Share2 size={16} className="mr-2" />
                  Share
                </Button>
                <Button size="sm" variant="outline" className="border-gray-300 text-gray-700 hover:bg-gray-50">
                  <FileText size={16} className="mr-2" />
                  Edit
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Recommendations */}
      <Card className="p-6 bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">💡 AI Recommendations</h3>
        <div className="space-y-4">
          {advisoryData.recommendations.map((rec, index) => (
            <div key={index} className="p-4 bg-white rounded-lg border border-blue-100">
              <div className="flex items-start gap-3">
                <div className="p-2 bg-blue-100 rounded-full">
                  <AlertCircle className="w-4 h-4 text-blue-600" />
                </div>
                <div className="flex-1">
                  <h4 className="font-semibold text-gray-900">{rec.category}</h4>
                  <p className="text-gray-700 mt-1">{rec.advice}</p>
                  <p className="text-sm text-gray-500 mt-2">Valid: {rec.validity}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Communication Channels */}
      <Card className="p-6 bg-gradient-to-br from-green-50 to-emerald-50 border-green-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">📡 Communication Channels</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {advisoryData.communication_channels.map((channel, index) => (
            <div key={index} className="p-4 bg-white rounded-lg border border-green-100 text-center">
              <div className="text-2xl mb-2">
                {channel === 'SMS' && '📱'}
                {channel === 'Email' && '📧'}
                {channel === 'Dashboard' && '🖥️'}
                {channel === 'Public Announcements' && '📣'}
              </div>
              <p className="font-medium text-gray-900">{channel}</p>
              <p className="text-sm text-gray-600">Active</p>
            </div>
          ))}
        </div>
      </Card>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-4 text-center bg-gradient-to-br from-red-50 to-red-100 border-red-200">
          <p className="text-2xl font-bold text-red-600">
            {advisoryData.current_alerts.filter(alert => alert.priority === 'high').length}
          </p>
          <p className="text-sm text-gray-700">High Priority Alerts</p>
        </Card>

        <Card className="p-4 text-center bg-gradient-to-br from-yellow-50 to-yellow-100 border-yellow-200">
          <p className="text-2xl font-bold text-yellow-600">
            {advisoryData.current_alerts.filter(alert => alert.priority === 'medium').length}
          </p>
          <p className="text-sm text-gray-700">Medium Priority Alerts</p>
        </Card>

        <Card className="p-4 text-center bg-gradient-to-br from-green-50 to-green-100 border-green-200">
          <p className="text-2xl font-bold text-green-600">
            {advisoryData.communication_channels.length}
          </p>
          <p className="text-sm text-gray-700">Active Channels</p>
        </Card>
      </div>

      <div className="text-center">
        <p className="text-xs text-gray-500">
          Data refreshes every 30 seconds • AI-powered advisory system
        </p>
      </div>
    </div>
  );
};
