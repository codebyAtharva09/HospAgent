import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { AlertTriangle, Package, TrendingDown, CheckCircle } from "lucide-react";
import { useState, useEffect } from "react";

const InventoryPanel = () => {
  const [inventoryData, setInventoryData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchInventoryData = async () => {
      try {
        setError(null);
        const response = await fetch('http://localhost:5000/api/inventory');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setInventoryData(data);
      } catch (err) {
        console.error('Error fetching inventory data:', err);
        setError('Failed to load inventory data. Please check if the backend is running.');
      } finally {
        setLoading(false);
      }
    };

    fetchInventoryData();
    const interval = setInterval(fetchInventoryData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="p-6 bg-white rounded-2xl shadow-lg">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="h-64 bg-gray-200 rounded mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-20 bg-gray-200 rounded"></div>
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

  const getStatusColor = (status) => {
    switch (status) {
      case 'adequate': return 'bg-green-100 text-green-800 border-green-200';
      case 'low': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default: return 'bg-red-100 text-red-800 border-red-200';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'adequate': return <CheckCircle size={12} className="mr-1" />;
      case 'low': return <AlertTriangle size={12} className="mr-1" />;
      default: return <AlertTriangle size={12} className="mr-1" />;
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">📦 Supply & Inventory</h2>
          <p className="text-gray-600">Real-time stock levels and AI-powered reorder alerts</p>
        </div>
        <Button className="bg-blue-500 hover:bg-blue-600 text-white shadow-md">
          <Package size={18} className="mr-2" />
          Manage Inventory
        </Button>
      </div>

      {/* Critical Alerts */}
      {inventoryData.alerts && inventoryData.alerts.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-gray-900">🚨 Critical Alerts</h3>
          {inventoryData.alerts.map((alert, index) => (
            <Card key={index} className="p-4 border-l-4 border-l-red-500 bg-red-50">
              <div className="flex items-start gap-3">
                <AlertTriangle className="text-red-600 flex-shrink-0 mt-0.5" size={20} />
                <div className="flex-1">
                  <h4 className="font-semibold text-gray-900">{alert.item}</h4>
                  <p className="text-sm text-gray-700 mt-1">{alert.message}</p>
                  <div className="flex items-center gap-3 mt-2">
                    <Badge variant="outline" className="bg-red-100 text-red-800 border-red-200">
                      Priority: {alert.priority}
                    </Badge>
                    <Button size="sm" className="bg-red-600 text-white hover:bg-red-700">
                      {alert.action_required}
                    </Button>
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Inventory Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Object.entries(inventoryData).filter(([key]) => key !== 'alerts').map(([key, item]) => (
          <Card key={key} className="p-6 bg-gradient-to-br from-white to-gray-50 border border-gray-200 hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 capitalize">{key}</h3>
              <Badge variant="outline" className={getStatusColor(item.status)}>
                {getStatusIcon(item.status)}
                {item.status}
              </Badge>
            </div>

            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-600">Current Stock</p>
                <p className="text-2xl font-bold text-gray-900">{item.current_stock || item.current}</p>
              </div>

              <div>
                <p className="text-sm text-gray-600">Daily Consumption</p>
                <p className="text-lg font-semibold text-gray-700">{item.daily_consumption}</p>
              </div>

              <div>
                <p className="text-sm text-gray-600">Reorder Point</p>
                <p className="text-lg font-semibold text-gray-700">{item.reorder_point}</p>
              </div>

              {item.supplier && (
                <div>
                  <p className="text-sm text-gray-600">Supplier</p>
                  <p className="text-sm font-medium text-gray-800">{item.supplier}</p>
                </div>
              )}

              <div className="pt-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Stock Level</span>
                  <span className={`font-medium ${item.current_stock < item.reorder_point ? 'text-red-600' : 'text-green-600'}`}>
                    {Math.round((item.current_stock / (item.reorder_point * 1.5)) * 100)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                  <div
                    className={`h-2 rounded-full ${item.current_stock < item.reorder_point ? 'bg-red-500' : 'bg-green-500'}`}
                    style={{ width: `${Math.min(100, (item.current_stock / (item.reorder_point * 1.5)) * 100)}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Summary Stats */}
      <Card className="p-6 bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 Inventory Summary</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="text-center">
            <p className="text-2xl font-bold text-blue-600">
              {Object.values(inventoryData).filter(item => item.status === 'adequate').length}
            </p>
            <p className="text-sm text-gray-600">Adequate Stock</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-yellow-600">
              {Object.values(inventoryData).filter(item => item.status === 'low').length}
            </p>
            <p className="text-sm text-gray-600">Low Stock</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-red-600">
              {inventoryData.alerts ? inventoryData.alerts.length : 0}
            </p>
            <p className="text-sm text-gray-600">Critical Alerts</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-green-600">
              {Object.values(inventoryData).reduce((sum, item) => sum + (item.daily_consumption || 0), 0)}
            </p>
            <p className="text-sm text-gray-600">Daily Consumption</p>
          </div>
        </div>
      </Card>

      <div className="text-center">
        <p className="text-xs text-gray-500">
          Data refreshes every 30 seconds • AI-powered inventory management
        </p>
      </div>
    </div>
  );
};

export { InventoryPanel };
