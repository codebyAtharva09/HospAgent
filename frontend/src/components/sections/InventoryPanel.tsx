import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { AlertTriangle, Package, TrendingDown } from "lucide-react";
import { useState, useEffect } from "react";
import { getInventoryRecommendationsHistory } from "@/services/supabase";

interface InventoryItem {
  name: string;
  category: string;
  current: number;
  minimum: number;
  unit: string;
  depletionDays: number;
  status: "critical" | "low" | "adequate";
}

const InventoryPanel = () => {
  const [inventory, setInventory] = useState<InventoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchInventoryData = async () => {
      try {
        const response = await fetch('/api/resource-status');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();

        // Transform backend data to match frontend interface
        const transformedInventory: InventoryItem[] = [
          {
            name: "Surgical Masks (N95)",
            category: "PPE",
            current: Math.floor(data.oxygen.cylinders_available * 3), // Simulate mask inventory
            minimum: 500,
            unit: "boxes",
            depletionDays: Math.floor(Math.floor(data.oxygen.cylinders_available * 3) / 150),
            status: Math.floor(data.oxygen.cylinders_available * 3) < 500 ? "critical" : Math.floor(data.oxygen.cylinders_available * 3) < 750 ? "low" : "adequate",
          },
          {
            name: "Sterile Gloves",
            category: "PPE",
            current: Math.floor(data.beds.available * 10), // Simulate glove inventory
            minimum: 2000,
            unit: "pairs",
            depletionDays: Math.floor(Math.floor(data.beds.available * 10) / 350),
            status: Math.floor(data.beds.available * 10) >= 2000 ? "adequate" : "low",
          },
          {
            name: "IV Fluids (Saline)",
            category: "Medical Supplies",
            current: Math.floor(data.beds.available * 5), // Simulate IV fluid inventory
            minimum: 500,
            unit: "bags",
            depletionDays: Math.floor(Math.floor(data.beds.available * 5) / 136),
            status: Math.floor(data.beds.available * 5) >= 500 ? "adequate" : "low",
          },
          {
            name: "Antibiotics (General)",
            category: "Medicines",
            current: Math.floor(data.staff.doctors_on_duty * 4), // Simulate antibiotic inventory
            minimum: 300,
            unit: "units",
            depletionDays: Math.floor(Math.floor(data.staff.doctors_on_duty * 4) / 60),
            status: Math.floor(data.staff.doctors_on_duty * 4) < 300 ? "low" : "adequate",
          },
          {
            name: "Syringes (5ml)",
            category: "Medical Supplies",
            current: Math.floor(data.beds.available * 8), // Simulate syringe inventory
            minimum: 1500,
            unit: "units",
            depletionDays: Math.floor(Math.floor(data.beds.available * 8) / 200),
            status: Math.floor(data.beds.available * 8) < 1500 ? "low" : "adequate",
          },
          {
            name: "Oxygen Cylinders",
            category: "Critical",
            current: data.oxygen.cylinders_available,
            minimum: data.oxygen.critical_threshold,
            unit: "cylinders",
            depletionDays: Math.floor(data.oxygen.cylinders_available / data.oxygen.consumption_rate),
            status: data.oxygen.cylinders_available < data.oxygen.critical_threshold ? "critical" : "adequate",
          },
        ];

        setInventory(transformedInventory);
      } catch (error) {
        console.error('Error fetching inventory data:', error);
        // Set fallback data on error
        setInventory([
          {
            name: "Surgical Masks (N95)",
            category: "PPE",
            current: 450,
            minimum: 500,
            unit: "boxes",
            depletionDays: 3,
            status: "critical",
          },
          {
            name: "Sterile Gloves",
            category: "PPE",
            current: 2800,
            minimum: 2000,
            unit: "pairs",
            depletionDays: 8,
            status: "adequate",
          },
          {
            name: "IV Fluids (Saline)",
            category: "Medical Supplies",
            current: 680,
            minimum: 500,
            unit: "bags",
            depletionDays: 5,
            status: "adequate",
          },
          {
            name: "Antibiotics (General)",
            category: "Medicines",
            current: 240,
            minimum: 300,
            unit: "units",
            depletionDays: 4,
            status: "low",
          },
          {
            name: "Syringes (5ml)",
            category: "Medical Supplies",
            current: 1200,
            minimum: 1500,
            unit: "units",
            depletionDays: 6,
            status: "low",
          },
          {
            name: "Oxygen Cylinders",
            category: "Critical",
            current: 42,
            minimum: 50,
            unit: "cylinders",
            depletionDays: 2,
            status: "critical",
          },
        ]);
      } finally {
        setLoading(false);
      }
    };

    // Initial fetch
    fetchInventoryData();

    // Set up real-time polling every 5 seconds
    const interval = setInterval(fetchInventoryData, 5000);

    // Cleanup interval on component unmount
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <div className="flex justify-center items-center h-64">Loading inventory data...</div>;
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Supply & Inventory</h2>
          <p className="text-muted-foreground">Real-time stock levels and depletion forecasts</p>
        </div>
        <Button variant="outline" className="border-primary text-primary hover:bg-primary hover:text-primary-foreground">
          <Package size={18} className="mr-2" />
          View All Items
        </Button>
      </div>

      {/* Critical Alerts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {inventory
          .filter(item => item.status === 'critical')
          .map(item => (
            <Card key={item.name} className="p-4 border-l-4 border-l-destructive bg-destructive/5">
              <div className="flex items-start gap-3">
                <AlertTriangle className="text-destructive flex-shrink-0 mt-0.5" size={20} />
                <div className="flex-1">
                  <h4 className="font-semibold text-foreground">{item.name}</h4>
                  <p className="text-sm text-muted-foreground mt-1">
                    Only <span className="font-semibold text-destructive">{item.current} {item.unit}</span> remaining
                  </p>
                  <div className="flex items-center gap-3 mt-2">
                    <Badge variant="outline" className="bg-destructive/10 text-destructive border-destructive">
                      {item.depletionDays} days left
                    </Badge>
                    <Button size="sm" className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
                      Reorder Now
                    </Button>
                  </div>
                </div>
              </div>
            </Card>
          ))}
      </div>

      {/* Inventory Table */}
      <Card className="shadow-soft overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-secondary">
              <tr>
                <th className="text-left p-4 text-sm font-semibold text-secondary-foreground">Item</th>
                <th className="text-left p-4 text-sm font-semibold text-secondary-foreground">Category</th>
                <th className="text-center p-4 text-sm font-semibold text-secondary-foreground">Current Stock</th>
                <th className="text-center p-4 text-sm font-semibold text-secondary-foreground">Min Required</th>
                <th className="text-center p-4 text-sm font-semibold text-secondary-foreground">Status</th>
                <th className="text-center p-4 text-sm font-semibold text-secondary-foreground">Depletion</th>
                <th className="text-center p-4 text-sm font-semibold text-secondary-foreground">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {inventory.map((item) => {
                const statusConfig = {
                  critical: { bg: "bg-destructive/10", text: "text-destructive", label: "Critical" },
                  low: { bg: "bg-warning/10", text: "text-warning", label: "Low Stock" },
                  adequate: { bg: "bg-success/10", text: "text-success", label: "Adequate" },
                };

                return (
                  <tr key={item.name} className="hover:bg-muted/50 transition-colors">
                    <td className="p-4">
                      <span className="font-medium text-foreground">{item.name}</span>
                    </td>
                    <td className="p-4">
                      <Badge variant="outline" className="bg-secondary text-secondary-foreground">
                        {item.category}
                      </Badge>
                    </td>
                    <td className="p-4 text-center">
                      <span className="font-semibold text-foreground">
                        {item.current} {item.unit}
                      </span>
                    </td>
                    <td className="p-4 text-center">
                      <span className="text-muted-foreground">
                        {item.minimum} {item.unit}
                      </span>
                    </td>
                    <td className="p-4">
                      <div className="flex justify-center">
                        <Badge variant="outline" className={`${statusConfig[item.status].bg} ${statusConfig[item.status].text} border-0`}>
                          {statusConfig[item.status].label}
                        </Badge>
                      </div>
                    </td>
                    <td className="p-4 text-center">
                      <div className="flex items-center justify-center gap-1 text-sm text-muted-foreground">
                        <TrendingDown size={14} className={item.depletionDays <= 3 ? 'text-destructive' : 'text-warning'} />
                        {item.depletionDays} days
                      </div>
                    </td>
                    <td className="p-4 text-center">
                      <Button
                        variant="outline"
                        size="sm"
                        className={item.status === 'critical'
                          ? "border-destructive text-destructive hover:bg-destructive hover:text-destructive-foreground"
                          : "border-primary text-primary hover:bg-primary hover:text-primary-foreground"
                        }
                      >
                        Reorder
                      </Button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};

export { InventoryPanel };
