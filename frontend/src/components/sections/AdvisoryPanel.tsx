import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Share2, FileText, MapPin, AlertCircle } from "lucide-react";
import { useState, useEffect } from "react";
import { getAdvisoriesHistory } from "@/services/supabase";

interface Advisory {
  id: string;
  title: string;
  content: string;
  priority: "high" | "medium" | "low";
  status: "draft" | "published";
  targetAreas: string[];
}

interface HeatmapItem {
  area: string;
  risk: "high" | "medium" | "low";
  cases: number;
}

export const AdvisoryPanel = () => {
  const [advisories, setAdvisories] = useState<Advisory[]>([]);
  const [heatmapData, setHeatmapData] = useState<HeatmapItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch advisories
        const alertsResponse = await fetch('/api/alerts');
        if (!alertsResponse.ok) {
          throw new Error(`Alerts API error! status: ${alertsResponse.status}`);
        }
        const alertsData = await alertsResponse.json();

        // Transform advisories
        const transformedAdvisories: Advisory[] = alertsData.alerts.map((item: any) => ({
          id: item.id,
          title: item.title,
          content: item.message,
          priority: item.priority,
          status: item.type === "General Advisory" ? "published" : "draft",
          targetAreas: item.affected_departments,
        }));

        setAdvisories(transformedAdvisories);

        // Fetch resource status for heatmap
        const resourceResponse = await fetch('/api/resource-status');
        if (!resourceResponse.ok) {
          throw new Error(`Resource API error! status: ${resourceResponse.status}`);
        }
        const resourceData = await resourceResponse.json();

        // Transform resource data into heatmap
        const transformedHeatmap: HeatmapItem[] = [
          {
            area: "Beds",
            risk: resourceData.beds.utilization_rate > 0.9 ? "high" as const :
                  resourceData.beds.utilization_rate > 0.8 ? "medium" as const : "low" as const,
            cases: resourceData.beds.occupied,
          },
          {
            area: "ICU",
            risk: resourceData.beds.icu_available < 20 ? "high" as const :
                  resourceData.beds.icu_available < 30 ? "medium" as const : "low" as const,
            cases: resourceData.beds.total - resourceData.beds.icu_available,
          },
          {
            area: "Oxygen",
            risk: resourceData.oxygen.status === "low" ? "high" as const : "low" as const,
            cases: resourceData.oxygen.cylinders_available,
          },
          {
            area: "Staff",
            risk: resourceData.staff.shift_coverage < 0.85 ? "high" as const :
                  resourceData.staff.shift_coverage < 0.9 ? "medium" as const : "low" as const,
            cases: resourceData.staff.doctors_on_duty + resourceData.staff.nurses_on_duty,
          },
        ];

        setHeatmapData(transformedHeatmap);
      } catch (error) {
        console.error('Error fetching data:', error);
        // Set fallback data on error
        setAdvisories([
          {
            id: "1",
            title: "Emergency Department Wait Times",
            content: "Current wait times in Emergency Department are 45-60 minutes due to high patient volume. Consider visiting nearby urgent care centers for non-critical conditions.",
            priority: "high",
            status: "draft",
            targetAreas: ["Emergency", "Public Website", "SMS Alerts"],
          },
          {
            id: "2",
            title: "Flu Vaccination Drive",
            content: "Free flu vaccination available at our hospital. Walk-ins welcome Monday-Friday 9 AM - 5 PM. Protect yourself and your family this season.",
            priority: "medium",
            status: "published",
            targetAreas: ["Public Website", "Social Media"],
          },
          {
            id: "3",
            title: "Visiting Hours Update",
            content: "ICU visiting hours temporarily adjusted to 2 PM - 4 PM and 7 PM - 9 PM to ensure optimal patient care and rest periods.",
            priority: "medium",
            status: "draft",
            targetAreas: ["Hospital Display", "Website"],
          },
        ]);
        setHeatmapData([
          { area: "Beds", risk: "high" as const, cases: 450 },
          { area: "ICU", risk: "medium" as const, cases: 18 },
          { area: "Oxygen", risk: "low" as const, cases: 120 },
          { area: "Staff", risk: "medium" as const, cases: 165 },
        ]);
      } finally {
        setLoading(false);
      }
    };

    // Initial fetch
    fetchData();

    // Set up real-time polling every 5 seconds
    const interval = setInterval(fetchData, 5000);

    // Cleanup interval on component unmount
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <div className="flex justify-center items-center h-64">Loading advisory data...</div>;
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h2 className="text-2xl font-bold text-foreground">Patient Advisory</h2>
        <p className="text-muted-foreground">Public communication and health alerts</p>
      </div>

      {/* Advisory Drafts */}
      <div className="space-y-4">
        {advisories.map((advisory) => {
          const priorityConfig = {
            high: { bg: "bg-destructive/10", text: "text-destructive", label: "High Priority" },
            medium: { bg: "bg-warning/10", text: "text-warning", label: "Medium Priority" },
            low: { bg: "bg-success/10", text: "text-success", label: "Low Priority" },
          };

          return (
            <Card key={advisory.id} className="p-5 shadow-soft">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-semibold text-foreground">{advisory.title}</h3>
                    <Badge
                      variant="outline"
                      className={`${priorityConfig[advisory.priority].bg} ${priorityConfig[advisory.priority].text} border-0`}
                    >
                      {priorityConfig[advisory.priority].label}
                    </Badge>
                    {advisory.status === 'published' && (
                      <Badge variant="outline" className="bg-primary/10 text-primary border-0">
                        Published
                      </Badge>
                    )}
                  </div>

                  <p className="text-sm text-muted-foreground mb-3">{advisory.content}</p>

                  <div className="flex flex-wrap gap-2">
                    {advisory.targetAreas.map((area) => (
                      <Badge key={area} variant="outline" className="bg-secondary text-secondary-foreground">
                        <MapPin size={12} className="mr-1" />
                        {area}
                      </Badge>
                    ))}
                  </div>
                </div>

                <div className="flex flex-col gap-2">
                  <Button size="sm" className="bg-gradient-primary shadow-medium hover:shadow-strong">
                    <Share2 size={16} className="mr-2" />
                    Publish
                  </Button>
                  <Button size="sm" variant="outline" className="border-primary text-primary hover:bg-primary hover:text-primary-foreground">
                    <FileText size={16} className="mr-2" />
                    Edit
                  </Button>
                </div>
              </div>
            </Card>
          );
        })}
      </div>

      {/* Health Heatmap */}
      <Card className="p-6 shadow-soft">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-foreground">Area Health Heatmap</h3>
          <Badge variant="outline" className="bg-accent/10 text-accent border-accent">
            Updated 2 hours ago
          </Badge>
        </div>

        <div className="space-y-3">
          {heatmapData.map((area) => {
            const riskConfig = {
              high: { bg: "bg-destructive", label: "High Risk" },
              medium: { bg: "bg-warning", label: "Medium Risk" },
              low: { bg: "bg-success", label: "Low Risk" },
            };

            return (
              <div key={area.area} className="flex items-center gap-4">
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-foreground">{area.area}</span>
                    <div className="flex items-center gap-3">
                      <span className="text-sm text-muted-foreground">{area.cases} cases</span>
                      <Badge variant="outline" className={`${riskConfig[area.risk].bg}/10 text-${riskConfig[area.risk].bg.replace('bg-', '')} border-0`}>
                        {riskConfig[area.risk].label}
                      </Badge>
                    </div>
                  </div>
                  <div className="h-2 bg-muted rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${riskConfig[area.risk].bg}`}
                      style={{ width: `${(area.cases / 160) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        <div className="mt-6 p-4 bg-accent/5 rounded-lg border border-accent/20">
          <div className="flex items-start gap-3">
            <AlertCircle className="text-accent flex-shrink-0 mt-0.5" size={18} />
            <div>
              <h4 className="font-semibold text-foreground text-sm">Recommendation</h4>
              <p className="text-sm text-muted-foreground mt-1">
                Issue preventive health advisory for North and Central zones. Consider mobile health camps in high-risk areas.
              </p>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};
