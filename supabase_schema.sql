-- Supabase SQL Schema for HospAgent
-- Run this in your Supabase SQL Editor

-- Create predictions table
CREATE TABLE predictions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    date DATE NOT NULL,
    predicted_patients INTEGER NOT NULL,
    aqi INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create recommendations table
CREATE TABLE recommendations (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    prediction_id UUID REFERENCES predictions(id),
    recommended_staff INTEGER NOT NULL DEFAULT 0,
    supplies_needed INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create advisories table
CREATE TABLE advisories (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    prediction_id UUID REFERENCES predictions(id),
    advisory_text TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security (RLS)
ALTER TABLE predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE advisories ENABLE ROW LEVEL SECURITY;

-- Create policies for anonymous access (adjust as needed for your security requirements)
CREATE POLICY "Allow anonymous read access on predictions" ON predictions FOR SELECT USING (true);
CREATE POLICY "Allow anonymous insert access on predictions" ON predictions FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow anonymous read access on recommendations" ON recommendations FOR SELECT USING (true);
CREATE POLICY "Allow anonymous insert access on recommendations" ON recommendations FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow anonymous read access on advisories" ON advisories FOR SELECT USING (true);
CREATE POLICY "Allow anonymous insert access on advisories" ON advisories FOR INSERT WITH CHECK (true);

-- Create indexes for better performance
CREATE INDEX idx_predictions_date ON predictions(date);
CREATE INDEX idx_predictions_event_type ON predictions(event_type);
CREATE INDEX idx_recommendations_prediction_id ON recommendations(prediction_id);
CREATE INDEX idx_advisories_prediction_id ON advisories(prediction_id);
