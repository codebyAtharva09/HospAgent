import { useState } from "react";
import { Sidebar } from "@/components/Sidebar";
import { OverviewPanel } from "@/components/sections/OverviewPanel";
import { PredictionPanel } from "@/components/sections/PredictionPanel";
import { StaffPanel } from "@/components/sections/StaffPanel";
import { InventoryPanel } from "@/components/sections/InventoryPanel";
import { AdvisoryPanel } from "@/components/sections/AdvisoryPanel";
import { ActivityPanel } from "@/components/sections/ActivityPanel";
import ForecastChart from "@/components/ForecastChart";

const Index = () => {
  const [activeSection, setActiveSection] = useState("forecast");

  const renderSection = () => {
    switch (activeSection) {
      case "overview":
        return <OverviewPanel />;
      case "forecast":
        return <ForecastChart />;
      case "predictions":
        return <PredictionPanel />;
      case "staff":
        return <StaffPanel />;
      case "inventory":
        return <InventoryPanel />;
      case "advisory":
        return <AdvisoryPanel />;
      case "activity":
        return <ActivityPanel />;
      default:
        return <ForecastChart />;
    }
  };

  return (
    <div className="flex min-h-screen bg-background w-full">
      <Sidebar activeSection={activeSection} onSectionChange={setActiveSection} />

      <main className="flex-1 overflow-auto">
        <div className="p-8 max-w-[1600px] mx-auto">
          {renderSection()}
        </div>
      </main>
    </div>
  );
};

export default Index;
