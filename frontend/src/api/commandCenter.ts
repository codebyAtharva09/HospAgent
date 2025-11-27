export interface CommandCenterResponse {
    env: {
        aqi: number;
        pm25: number;
        temp_c: number;
        weather_label: string;
    };
    risk: {
        index: number;
        level: string;
    };
    risk_analysis: {
        factors: string[];
        confidence: number;
    };
    staffing: {
        today: {
            required: { doctors: number; nurses: number };
            available: { doctors: number; nurses: number };
            shortage: { doctors: number; nurses: number };
        };
    };
    supplies: {
        name: string;
        status: string;
        available?: number;
        required?: number;
    }[];
    festival: {
        name: string | null;
        date: string | null;
        risk_level: string | null;
        is_tomorrow: boolean;
        advisory: string | null;
    };
    forecast: {
        days: { date: string; total: number; respiratory: number }[];
        peak_load: number;
        avg_respiratory: number;
    };
    hospital_overview: {
        total_doctors: number;
        total_nurses: number;
        total_beds: number;
        icu_beds: number;
        ventilators: number;
        ambulances: number;
    };
    wellbeing?: {
        burnout_risk_level: string;
        note: string;
    };
}

export interface FestivalEvent {
    id: string;
    summary: string;
    date: string;
    source: string;
    high_risk: boolean;
}

export async function getCommandCenter(): Promise<CommandCenterResponse> {
    const base = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    const res = await fetch(`${base}/api/command-center`);
    if (!res.ok) throw new Error("Failed to fetch command center");
    return res.json();
}

export async function getUpcomingFestivals(days: number = 60): Promise<FestivalEvent[]> {
    const base = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    const res = await fetch(`${base}/api/festivals/upcoming?days_ahead=${days}`);
    if (!res.ok) throw new Error("Failed to fetch festivals");
    return res.json();
}
