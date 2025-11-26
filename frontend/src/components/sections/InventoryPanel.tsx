import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Package, AlertTriangle, CheckCircle, ArrowDown, ArrowUp } from "lucide-react";
import api from "@/services/api";

interface InventoryItem {
  current_stock: number;
  daily_consumption: number;
  reorder_point: number;
  status: 'adequate' | 'low' | 'critical';
  supplier?: string;
  current?: number; // Handle potential API inconsistency
}

interface InventoryData {
  medications: InventoryItem;
  surgical_kits: InventoryItem;
  oxygen_cylinders: InventoryItem;
  ppe_kits: InventoryItem;
  alerts?: Array<{
    item: string;
    message: string;
    action_required: string;
    priority: string;
  }>;
}

const InventoryPanel = () => {
  const [inventoryData, setInventoryData] = useState<InventoryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchInventoryData = async () => {
      try {
        const response = await api.get('/inventory');
        setInventoryData(response.data);
        setError(null);
      } catch (err) {
        console.error('Error fetching inventory data:', err);
        setError('Failed to load inventory data');
      } finally {
        setLoading(false);
      }
    };

    fetchInventoryData();
    const interval = setInterval(fetchInventoryData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="p-4 text-muted-foreground animate-pulse">Loading inventory...</div>;
  if (error) return <div className="p-4 text-rose-500 bg-rose-500/10 rounded-lg border border-rose-500/20">{error}</div>;
  if (!inventoryData) return null;

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'adequate': return 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20';
      case 'low': return 'bg-amber-500/10 text-amber-500 border-amber-500/20';
      case 'critical': return 'bg-rose-500/10 text-rose-500 border-rose-500/20';
      default: return 'bg-slate-500/10 text-slate-500 border-slate-500/20';
    }
  };

  return (
    <div className="space-y-6 h-full flex flex-col">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold flex items-center gap-2">
          <Package className="h-5 w-5 text-purple-500" />
          Inventory Status
        </h2>
        <Badge variant="outline" className="bg-purple-500/10 text-purple-500 border-purple-500/20">
          Real-time Stock
        </Badge>
      </div>

      {/* Alerts Section */}
      {inventoryData.alerts && inventoryData.alerts.length > 0 && (
        <div className="space-y-3">
          {inventoryData.alerts.map((alert, index) => (
            <div key={index} className="p-4 rounded-lg bg-rose-500/10 border border-rose-500/20 flex items-start gap-3">
              <AlertTriangle className="h-5 w-5 text-rose-500 shrink-0 mt-0.5" />
              <div className="flex-1">
                <h4 className="font-medium text-rose-500">{alert.item}: {alert.message}</h4>
                <p className="text-sm text-rose-400/80 mt-1">{alert.action_required}</p>
              </div>
              <Button size="sm" variant="outline" className="border-rose-500/30 text-rose-500 hover:bg-rose-500/20">
                Order Now
              </Button>
            </div>
          ))}
        </div>
      )}

      {/* Inventory Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {Object.entries(inventoryData).filter(([key]) => key !== 'alerts').map(([key, item]: [string, any]) => (
          <Card key={key} className="p-4 backdrop-blur-md bg-white/5 border-white/10 shadow-lg hover:bg-white/10 transition-colors">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="font-medium capitalize text-muted-foreground">{key.replace('_', ' ')}</h3>
                <div className="flex items-baseline gap-2 mt-1">
                  <span className="text-2xl font-bold">{item.current_stock || item.current}</span>
                  <span className="text-sm text-muted-foreground">units</span>
                </div>
              </div>
              <Badge variant="outline" className={getStatusColor(item.status)}>
                {item.status}
              </Badge>
            </div>

            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Daily Usage</span>
                <span className="font-medium">{item.daily_consumption} / day</span>
              </div>

              <div className="space-y-1">
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>Stock Level</span>
                  <span>{Math.round(((item.current_stock || item.current) / (item.reorder_point * 2)) * 100)}%</span>
                </div>
                <div className="h-1.5 w-full bg-white/10 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${item.status === 'critical' ? 'bg-rose-500' :
                        item.status === 'low' ? 'bg-amber-500' : 'bg-emerald-500'
                      }`}
                    style={{ width: `${Math.min(100, ((item.current_stock || item.current) / (item.reorder_point * 2)) * 100)}%` }}
                  />
                </div>
              </div>

              <div className="pt-2 border-t border-white/5 flex justify-between items-center">
                <span className="text-xs text-muted-foreground">Reorder at {item.reorder_point}</span>
                {item.supplier && (
                  <span className="text-xs text-muted-foreground flex items-center gap-1">
                    <Package className="h-3 w-3" /> {item.supplier}
                  </span>
                )}
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};

export { InventoryPanel };
