export interface DoctorSpecialization {
    name: string;
    count: number;
}

export interface HospitalOverviewResponse {
    total_doctors: number;
    total_nurses: number;
    total_beds: number;
    icu_beds: number;
    ventilators: number;
    ambulances: number;
    wards: number;
    operating_theaters: number;
    doctors_by_specialization: DoctorSpecialization[];
    // New fields
    current_inpatients?: number;
    icus_occupied?: number;
    wards_occupied?: number;
}

export async function getHospitalOverview(): Promise<HospitalOverviewResponse> {
    const base = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    const res = await fetch(`${base}/api/hospital-overview`);
    if (!res.ok) throw new Error("Failed to fetch hospital overview");
    return res.json();
}
