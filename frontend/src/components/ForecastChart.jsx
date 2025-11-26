import React, { useEffect, useState } from "react";
import api from "@/services/api";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, AreaChart, Area
} from "recharts";
import { Card } from "@/components/ui/card";
import { TrendingUp } from "lucide-react";

export default function ForecastChart() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      setError(null);
      const res = await api.get("/forecast");
      const normalized = res.data.map((item) => ({
        date: new Date(item.date).toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric'
        }),
        fullDate: item.date,
        predicted_inflow: item.predicted_patients,
        confidence: item.confidence || 85, // Default confidence if missing
      }));
      setData(normalized);
      setLoading(false);
    } catch (err) {
      console.error("Error fetching forecast:", err);
      setError("Failed to load forecast data");
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    // Auto-refresh every 30 seconds instead of 5 for better UX
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return (
    <div className="flex items-center justify-center h-[400px]">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto mb-4"></div>
        <p className="text-muted-foreground">Loading forecast...</p>
      </div>
    </div>
  );

  if (error) return (
    <div className="p-6 text-rose-500 bg-rose-500/10 rounded-lg border border-rose-500/20 backdrop-blur-sm">
      <p className="font-semibold mb-2">⚠️ Error Loading Forecast</p>
      <p className="text-sm">{error}</p>
    </div>
  );

  return (
    <div className="flex flex-col space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold flex items-center gap-2">
          <TrendingUp className="h-5 w-5 text-indigo-500" />
          7-Day Forecast
        </h2>
        <div className="flex items-center gap-2">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-500"></span>
          </span>
          <span className="text-xs font-medium text-indigo-500">AI Model Active</span>
        </div>
      </div>

      <div className="h-[300px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 5, right: 0, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="colorInflow" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
            <XAxis
              dataKey="date"
              stroke="#888888"
              fontSize={12}
              tickLine={false}
              axisLine={false}
            />
            <YAxis
              stroke="#888888"
              fontSize={12}
              tickLine={false}
              axisLine={false}
              domain={[0, 'dataMax + 50']}
              tickFormatter={(value) => Math.round(value).toString()}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'rgba(255, 255, 255, 0.9)',
                border: 'none',
                borderRadius: '8px',
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
              }}
            />
            <Area
              type="monotone"
              dataKey="predicted_inflow"
              stroke="#6366f1"
              strokeWidth={3}
              fillOpacity={1}
              fill="url(#colorInflow)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-3 sm:grid-cols-4 lg:grid-cols-7 gap-2">
        {data.map((item, i) => (
          <div
            key={item.fullDate}
            className="p-3 rounded-xl bg-white/5 border border-white/10 text-center hover:bg-white/10 hover:border-indigo-500/30 transition-all duration-300 hover:-translate-y-1 backdrop-blur-sm group"
          >
            <p className="text-[10px] text-muted-foreground mb-1.5 group-hover:text-indigo-400 transition-colors">{item.date}</p>
            <p className="text-base font-bold bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">{item.predicted_inflow}</p>
            <p className="text-[9px] text-muted-foreground mt-0.5">patients</p>
          </div>
        ))}
      </div>
    </div>
  );
}
