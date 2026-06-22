-- 1. Create users table
CREATE TABLE IF NOT EXISTS users (
  electricity_id TEXT PRIMARY KEY DEFAULT 'ELEC-' || LPAD(FLOOR(RANDOM() * 900000 + 100000)::TEXT, 6, '0'),
  name TEXT NOT NULL,
  phone_number TEXT NOT NULL,
  nic_number TEXT NOT NULL UNIQUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Create usage table
CREATE TABLE IF NOT EXISTS usage (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  electricity_id TEXT REFERENCES users(electricity_id) ON DELETE CASCADE,
  units NUMERIC NOT NULL CHECK (units >= 0),
  month VARCHAR(7) NOT NULL CHECK (month ~ '^\d{4}-\d{2}$'),
  price NUMERIC NOT NULL CHECK (price >= 0),
  paid_amount NUMERIC DEFAULT 0 CHECK (paid_amount >= 0),
  balance NUMERIC NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (electricity_id, month)
);

-- 3. Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage ENABLE ROW LEVEL SECURITY;

-- 4. Allow public read
CREATE POLICY "Allow public read users" ON users FOR SELECT USING (true);
CREATE POLICY "Allow public insert users" ON users FOR INSERT WITH CHECK (true);