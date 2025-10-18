-- Create department_status table
CREATE TABLE IF NOT EXISTS department_status (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    occupancy INTEGER NOT NULL CHECK (occupancy >= 0 AND occupancy <= 100),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for better query performance
CREATE INDEX IF NOT EXISTS idx_department_status_name ON department_status(name);

-- Insert sample data
INSERT INTO department_status (name, occupancy) VALUES
    ('Emergency', 85),
    ('ICU', 92),
    ('Surgery', 71),
    ('Pediatrics', 54),
    ('General Ward', 67)
ON CONFLICT (name) DO UPDATE SET
    occupancy = EXCLUDED.occupancy,
    updated_at = NOW();

-- Enable Row Level Security (RLS)
ALTER TABLE department_status ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations for authenticated users
CREATE POLICY "Allow all operations for authenticated users" ON department_status
    FOR ALL USING (auth.role() = 'authenticated');

-- Create policy to allow read operations for anonymous users (for demo purposes)
CREATE POLICY "Allow read operations for anonymous users" ON department_status
    FOR SELECT USING (true);
