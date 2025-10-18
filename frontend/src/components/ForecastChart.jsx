import React, { useEffect, useState } from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from "recharts";

export default function ForecastChart() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      setError(null);
      const res = await axios.get("http://localhost:5000/api/forecast");
      const normalized = res.data.map((item) => ({
        date: new Date(item.date).toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric'
        }),
        fullDate: item.date,
        predicted_inflow: item.predicted_inflow,
        confidence: item.confidence,
      }));
      setData(normalized);
      setLoading(false);
    } catch (err) {
      console.error("Error fetching forecast:", err);
      setError("Failed to load forecast data. Please check if the backend is running.");
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    // Auto-refresh every 30 seconds instead of 5 for better UX
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);



  if (loading) {
    return (
      <div className="p-6 bg-white rounded-2xl shadow-lg">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="h-64 bg-gray-200 rounded mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[...Array(7)].map((_, i) => (
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
            onClick={fetchData}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-white rounded-2xl shadow-lg">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-semibold text-gray-900">📊 7-Day Patient Flow Forecast</h2>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <p className="text-sm text-gray-500">Live Data</p>
        </div>
      </div>

      <div className="w-full h-72 mb-6">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis
              dataKey="date"
              stroke="#6b7280"
              fontSize={12}
            />
            <YAxis
              yAxisId="left"
              stroke="#6b7280"
              fontSize={12}
              label={{ value: 'Patients', angle: -90, position: 'insideLeft' }}
            />
            <YAxis
              yAxisId="right"
              orientation="right"
              stroke="#6b7280"
              fontSize={12}
              domain={[0, 100]}
              label={{ value: 'Confidence %', angle: 90, position: 'insideRight' }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#f9fafb',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
              }}
              formatter={(value, name) => [
                name === 'Predicted Patients' ? `${value} patients` : `${value}%`,
                name
              ]}
            />
            <Legend />
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="predicted_inflow"
              stroke="#3b82f6"
              strokeWidth={3}
              name="Predicted Patients"
              dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6, stroke: '#3b82f6', strokeWidth: 2 }}
            />
            <Line
              yAxisId="right"
              type="monotone"
              dataKey="confidence"
              stroke="#10b981"
              strokeWidth={2}
              name="Confidence (%)"
              dot={{ fill: '#10b981', strokeWidth: 2, r: 3 }}
              strokeDasharray="5 5"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-7 gap-4">
        {data.map((item, i) => (
          <div
            key={item.fullDate}
            className="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg border border-blue-100 text-center hover:shadow-md transition-shadow"
          >
            <p className="text-sm font-medium text-gray-600 mb-1">{item.date}</p>
            <h3 className="text-xl font-bold text-gray-900 mb-1">{item.predicted_inflow}</h3>
            <p className="text-xs text-gray-500 mb-2">patients expected</p>
            <div className="flex items-center justify-center space-x-1">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <p className="text-xs font-medium text-green-600">{item.confidence}%</p>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 text-center">
        <p className="text-xs text-gray-500">
          Data refreshes every 30 seconds • Powered by AI forecasting
        </p>
      </div>
    </div>
  );
}
