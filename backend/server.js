import express from "express";
import cors from "cors";
import { createClient } from "@supabase/supabase-js";
import dotenv from "dotenv";

// Load environment variables
dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors({ origin: "*" }));
app.use(express.json());

// Supabase client
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseKey) {
  console.error("❌ Error: SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env file");
  process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseKey);

// Health check endpoint
app.get("/api/health", (req, res) => {
  res.json({ status: "OK", message: "Patient Surge Prediction API is running" });
});

// Fetch latest 7 forecast entries
app.get("/api/forecast", async (req, res) => {
  try {
    const { data, error } = await supabase
      .from("forecast_logs")
      .select("*")
      .order("date", { ascending: true })
      .limit(7);

    if (error) {
      console.error("Supabase error:", error);
      return res.status(500).json({ error: error.message });
    }

    res.json(data);
  } catch (err) {
    console.error("Server error:", err);
    res.status(500).json({ error: "Internal server error" });
  }
});

// Get forecast summary statistics
app.get("/api/forecast/summary", async (req, res) => {
  try {
    const { data, error } = await supabase
      .from("forecast_logs")
      .select("predicted_inflow, confidence")
      .order("date", { ascending: true })
      .limit(7);

    if (error) {
      console.error("Supabase error:", error);
      return res.status(500).json({ error: error.message });
    }

    if (!data || data.length === 0) {
      return res.json({
        total_predicted: 0,
        average_confidence: 0,
        max_inflow: 0,
        min_inflow: 0
      });
    }

    const total_predicted = data.reduce((sum, item) => sum + item.predicted_inflow, 0);
    const average_confidence = data.reduce((sum, item) => sum + item.confidence, 0) / data.length;
    const inflows = data.map(item => item.predicted_inflow);
    const max_inflow = Math.max(...inflows);
    const min_inflow = Math.min(...inflows);

    res.json({
      total_predicted,
      average_confidence: Math.round(average_confidence * 100) / 100,
      max_inflow,
      min_inflow
    });
  } catch (err) {
    console.error("Server error:", err);
    res.status(500).json({ error: "Internal server error" });
  }
});

// Staff allocation endpoint
app.get("/api/staff", async (req, res) => {
  try {
    // For now, return mock data. In production, fetch from Supabase or Flask backend
    const staffData = {
      doctors: {
        total: 85,
        on_duty: 62,
        available: 23,
        recommended: 68
      },
      nurses: {
        total: 150,
        on_duty: 125,
        available: 25,
        recommended: 135
      },
      technicians: {
        total: 45,
        on_duty: 38,
        available: 7,
        recommended: 42
      },
      allocation: [
        { department: "Emergency", doctors: 12, nurses: 25, technicians: 8 },
        { department: "ICU", doctors: 8, nurses: 18, technicians: 6 },
        { department: "General Ward", doctors: 15, nurses: 35, technicians: 10 },
        { department: "OPD", doctors: 18, nurses: 30, technicians: 12 },
        { department: "Surgery", doctors: 15, nurses: 27, technicians: 6 }
      ]
    };
    res.json(staffData);
  } catch (err) {
    console.error("Server error:", err);
    res.status(500).json({ error: "Internal server error" });
  }
});

// Inventory status endpoint
app.get("/api/inventory", async (req, res) => {
  try {
    // Mock inventory data
    const inventoryData = {
      oxygen: {
        current_stock: 120,
        daily_consumption: 35,
        reorder_point: 80,
        status: "adequate",
        supplier: "Medical Gases Ltd"
      },
      masks: {
        current_stock: 2500,
        daily_consumption: 180,
        reorder_point: 1000,
        status: "adequate",
        supplier: "Health Supplies Co"
      },
      gloves: {
        current_stock: 800,
        daily_consumption: 120,
        reorder_point: 500,
        status: "low",
        supplier: "MediEquip"
      },
      syringes: {
        current_stock: 1500,
        daily_consumption: 95,
        reorder_point: 800,
        status: "adequate",
        supplier: "PharmaCorp"
      },
      medications: {
        current_stock: 95,
        daily_consumption: 25,
        reorder_point: 60,
        status: "adequate",
        supplier: "MediPharm"
      },
      alerts: [
        {
          item: "Surgical Gloves",
          message: "Stock below reorder point",
          priority: "high",
          action_required: "Reorder immediately"
        }
      ]
    };
    res.json(inventoryData);
  } catch (err) {
    console.error("Server error:", err);
    res.status(500).json({ error: "Internal server error" });
  }
});

// Patient advisory endpoint
app.get("/api/advisory", async (req, res) => {
  try {
    // Mock advisory data
    const advisoryData = {
      current_alerts: [
        {
          id: 1,
          type: "Air Quality",
          title: "Poor Air Quality Alert",
          message: "High AQI levels detected. Respiratory patients should limit outdoor exposure.",
          priority: "medium",
          target_audience: "patients",
          timestamp: new Date().toISOString()
        },
        {
          id: 2,
          type: "Patient Surge",
          title: "Increased Wait Times",
          message: "Emergency Department experiencing higher than normal patient volume.",
          priority: "high",
          target_audience: "public",
          timestamp: new Date(Date.now() - 3600000).toISOString()
        }
      ],
      recommendations: [
        {
          category: "Respiratory Patients",
          advice: "Wear masks when outdoors, avoid strenuous activities",
          validity: "Until AQI improves"
        },
        {
          category: "General Public",
          advice: "Visit hospital only for emergencies during peak hours",
          validity: "Next 48 hours"
        }
      ],
      communication_channels: ["SMS", "Email", "Dashboard", "Public Announcements"]
    };
    res.json(advisoryData);
  } catch (err) {
    console.error("Server error:", err);
    res.status(500).json({ error: "Internal server error" });
  }
});

// AI Activity endpoint
app.get("/api/activity", async (req, res) => {
  try {
    // Mock AI activity data
    const activityData = {
      recent_predictions: [
        {
          timestamp: new Date().toISOString(),
          type: "Patient Surge Prediction",
          confidence: 0.92,
          result: "High surge expected tomorrow",
          status: "completed"
        },
        {
          timestamp: new Date(Date.now() - 1800000).toISOString(),
          type: "Staff Optimization",
          confidence: 0.88,
          result: "Recommended 15% increase in nursing staff",
          status: "completed"
        }
      ],
      model_performance: {
        accuracy: 0.94,
        precision: 0.89,
        recall: 0.91,
        last_updated: new Date(Date.now() - 86400000).toISOString()
      },
      active_processes: [
        {
          name: "Real-time Data Processing",
          status: "running",
          progress: 100
        },
        {
          name: "Model Retraining",
          status: "scheduled",
          next_run: new Date(Date.now() + 86400000).toISOString()
        }
      ],
      system_health: {
        status: "healthy",
        uptime: "7 days, 14 hours",
        last_backup: new Date(Date.now() - 43200000).toISOString()
      }
    };
    res.json(activityData);
  } catch (err) {
    console.error("Server error:", err);
    res.status(500).json({ error: "Internal server error" });
  }
});

// Overview/Dashboard endpoint
app.get("/api/overview", async (req, res) => {
  try {
    // Mock overview data
    const overviewData = {
      hospital_status: {
        total_beds: 500,
        occupied_beds: 387,
        available_beds: 113,
        utilization_rate: 0.77
      },
      patient_stats: {
        current_patients: 387,
        admitted_today: 45,
        discharged_today: 38,
        average_stay: 4.2
      },
      department_status: [
        { name: "Emergency", patients: 28, capacity: 30, status: "high" },
        { name: "ICU", patients: 18, capacity: 20, status: "normal" },
        { name: "General Ward", patients: 156, capacity: 200, status: "normal" },
        { name: "OPD", patients: 185, capacity: 250, status: "normal" }
      ],
      alerts_count: 3,
      last_updated: new Date().toISOString()
    };
    res.json(overviewData);
  } catch (err) {
    console.error("Server error:", err);
    res.status(500).json({ error: "Internal server error" });
  }
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: "Something went wrong!" });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: "Endpoint not found" });
});

app.listen(PORT, () => {
  console.log(`✅ Backend server running on port ${PORT}`);
  console.log(`📊 API endpoints:`);
  console.log(`   GET /api/health`);
  console.log(`   GET /api/forecast`);
  console.log(`   GET /api/forecast/summary`);
  console.log(`   GET /api/staff`);
  console.log(`   GET /api/inventory`);
  console.log(`   GET /api/advisory`);
  console.log(`   GET /api/activity`);
  console.log(`   GET /api/overview`);
});
