import { Activity, BarChart3, Users, Package, MessageSquare, TrendingUp, Menu, Zap } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";

interface NavItem {
  id: string;
  label: string;
  icon: React.ElementType;
}

const navItems: NavItem[] = [
  { id: "overview", label: "Overview", icon: BarChart3 },
  { id: "forecast", label: "AI Forecast", icon: Zap },
  { id: "predictions", label: "Patient Surge", icon: TrendingUp },
  { id: "staff", label: "Staff Allocation", icon: Users },
  { id: "inventory", label: "Supply & Inventory", icon: Package },
  { id: "advisory", label: "Patient Advisory", icon: MessageSquare },
  { id: "activity", label: "AI Activity", icon: Activity },
];

interface SidebarProps {
  activeSection: string;
  onSectionChange: (section: string) => void;
}

export const Sidebar = ({ activeSection, onSectionChange }: SidebarProps) => {
  const [isCollapsed, setIsCollapsed] = useState(false);

  return (
    <aside
      className={cn(
        "h-screen bg-card border-r border-border shadow-soft transition-all duration-300",
        isCollapsed ? "w-16" : "w-64"
      )}
    >
      <div className="flex flex-col h-full">
        {/* Header */}
        <div className="p-4 border-b border-border bg-gradient-primary">
          <div className="flex items-center justify-between">
            {!isCollapsed && (
              <h1 className="text-lg font-semibold text-primary-foreground">
                HospAgent AI
              </h1>
            )}
            <button
              onClick={() => setIsCollapsed(!isCollapsed)}
              className="p-2 rounded-lg hover:bg-primary-glow/20 text-primary-foreground transition-colors"
            >
              <Menu size={20} />
            </button>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeSection === item.id;

            return (
              <button
                key={item.id}
                onClick={() => onSectionChange(item.id)}
                className={cn(
                  "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200",
                  isActive
                    ? "bg-primary text-primary-foreground shadow-medium"
                    : "text-muted-foreground hover:bg-secondary hover:text-secondary-foreground"
                )}
              >
                <Icon size={20} className="flex-shrink-0" />
                {!isCollapsed && (
                  <span className="font-medium text-sm">{item.label}</span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-border">
          <div className={cn("flex items-center gap-3", isCollapsed && "justify-center")}>
            <div className="w-8 h-8 rounded-full bg-gradient-primary flex items-center justify-center text-primary-foreground font-semibold text-sm">
              AI
            </div>
            {!isCollapsed && (
              <div className="flex-1">
                <p className="text-xs font-medium text-foreground">AI System</p>
                <p className="text-xs text-muted-foreground">Active</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </aside>
  );
};
