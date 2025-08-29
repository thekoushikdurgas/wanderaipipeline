-- Create the places table for Supabase PostgreSQL
-- Run this script in the Supabase SQL Editor

CREATE TABLE IF NOT EXISTS places (
    place_id SERIAL PRIMARY KEY,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    types TEXT NOT NULL,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    pincode TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_places_name ON places(name);
CREATE INDEX IF NOT EXISTS idx_places_types ON places(types);
CREATE INDEX IF NOT EXISTS idx_places_created_at ON places(created_at);

-- Enable Row Level Security (RLS) - optional
-- ALTER TABLE places ENABLE ROW LEVEL SECURITY;

-- Create a policy to allow all operations (for development)
-- CREATE POLICY "Allow all operations" ON places FOR ALL USING (true);

-- Insert some sample data (optional)
INSERT INTO places (latitude, longitude, types, name, address, pincode) VALUES
(40.7128, -74.0060, 'tourist_attraction', 'Statue of Liberty', 'Liberty Island, New York, NY', '10004'),
(34.0522, -118.2437, 'restaurant', 'In-N-Out Burger', '7000 Sunset Blvd, Los Angeles, CA', '90028'),
(51.5074, -0.1278, 'hotel', 'The Ritz London', '150 Piccadilly, St. James''s, London', 'W1J 9BR'),
(35.6762, 139.6503, 'tourist_attraction', 'Tokyo Tower', '4 Chome-2-8 Shibakoen, Minato City, Tokyo', '105-0011'),
(48.8584, 2.2945, 'tourist_attraction', 'Eiffel Tower', 'Champ de Mars, 5 Avenue Anatole France, Paris', '75007')
ON CONFLICT DO NOTHING;
