-- Create forecast_logs table for storing AI forecast data
create table if not exists forecast_logs (
  id uuid primary key default uuid_generate_v4(),
  date date not null,
  predicted_inflow int not null,
  confidence numeric(5,2) not null check (confidence >= 0 and confidence <= 100),
  created_at timestamp default now()
);

-- Create index on date for faster queries
create index if not exists idx_forecast_logs_date on forecast_logs(date);

-- Enable Row Level Security (RLS)
alter table forecast_logs enable row level security;

-- Create policy to allow authenticated users to read forecast data
create policy "Allow authenticated users to read forecast_logs" on forecast_logs
  for select using (auth.role() = 'authenticated');

-- Create policy to allow service role to insert/update forecast data
create policy "Allow service role to manage forecast_logs" on forecast_logs
  for all using (auth.role() = 'service_role');
