-- Create the places table for Supabase PostgreSQL
-- Run this script in the Supabase SQL Editor

CREATE TABLE IF NOT EXISTS places (
    id TEXT PRIMARY KEY,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    types TEXT NOT NULL,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    pincode TEXT NOT NULL,
    rating FLOAT4 DEFAULT 0.0,
    followers FLOAT4 DEFAULT 0.0,
    country VARCHAR(100) DEFAULT 'Unknown',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_places_name ON places(name);
CREATE INDEX IF NOT EXISTS idx_places_types ON places(types);
CREATE INDEX IF NOT EXISTS idx_places_created_at ON places(created_at);
CREATE INDEX IF NOT EXISTS idx_places_rating ON places(rating);
CREATE INDEX IF NOT EXISTS idx_places_country ON places(country);
CREATE INDEX IF NOT EXISTS idx_places_pincode ON places(pincode);

-- Enable Row Level Security (RLS) - optional
-- ALTER TABLE places ENABLE ROW LEVEL SECURITY;

-- Create a policy to allow all operations (for development)
-- CREATE POLICY "Allow all operations" ON places FOR ALL USING (true);

-- Function to validate pincode format (supports pincodes less than 10 characters)
CREATE OR REPLACE FUNCTION validate_pincode(pincode_input TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    -- Check if pincode is less than 10 characters and contains only digits
    IF length(pincode_input) < 10 AND pincode_input ~ '^[0-9]+$' THEN
        RETURN TRUE;
    ELSE
        RETURN FALSE;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Function to format pincode (validate and clean numeric pincodes)
CREATE OR REPLACE FUNCTION format_pincode(pincode_input TEXT)
RETURNS TEXT AS $$
BEGIN
    -- Remove any spaces and convert to uppercase
    pincode_input := upper(regexp_replace(pincode_input, '\s+', '', 'g'));
    
    -- If it's all digits, validate length (must be less than 10)
    IF pincode_input ~ '^[0-9]+$' THEN
        -- Keep as is if less than 10 characters, truncate if longer
        IF length(pincode_input) >= 10 THEN
            pincode_input := left(pincode_input, 9);
        END IF;
    -- If it's alphanumeric, convert to digits only and validate
    ELSIF pincode_input ~ '^[A-Z0-9]+$' THEN
        -- Extract only digits
        pincode_input := regexp_replace(pincode_input, '[^0-9]', '', 'g');
        -- Truncate if longer than 9 digits
        IF length(pincode_input) >= 10 THEN
            pincode_input := left(pincode_input, 9);
        END IF;
    END IF;
    
    RETURN pincode_input;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically format pincode before insert/update
CREATE OR REPLACE FUNCTION format_pincode_trigger()
RETURNS TRIGGER AS $$
BEGIN
    -- Format pincode before insert/update
    NEW.pincode := format_pincode(NEW.pincode);
    
    -- Validate the formatted pincode
    IF NOT validate_pincode(NEW.pincode) THEN
        RAISE EXCEPTION 'Invalid pincode format. Must be less than 10 characters and contain only digits.';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for automatic pincode formatting
DROP TRIGGER IF EXISTS trigger_format_pincode ON places;
CREATE TRIGGER trigger_format_pincode
    BEFORE INSERT OR UPDATE ON places
    FOR EACH ROW
    EXECUTE FUNCTION format_pincode_trigger();

-- Insert some sample data (optional) - using various pincode lengths (less than 10 characters)
INSERT INTO places (id,latitude, longitude, types, name, address, pincode, rating, followers, country) VALUES
( 'ola-platform:5000046837683',40.7128, -74.0060, 'tourist_attraction', 'Statue of Liberty', 'Liberty Island, New York, NY', '10004', 4.5, 15000, 'United States'),
('ola-platform:5000046837684',34.0522, -118.2437, 'restaurant', 'In-N-Out Burger', '7000 Sunset Blvd, Los Angeles, CA', '90028', 4.2, 8500, 'United States'),
('ola-platform:5000046837685',51.5074, -0.1278, 'hotel', 'The Ritz London', '150 Piccadilly, St. James''s, London', 'SW1A1A', 4.8, 22000, 'United Kingdom'),
('ola-platform:5000046837686',35.6762, 139.6503, 'tourist_attraction', 'Tokyo Tower', '4 Chome-2-8 Shibakoen, Minato City, Tokyo', '105001', 4.3, 12000, 'Japan'),
('ola-platform:5000046837687',48.8584, 2.2945, 'tourist_attraction', 'Eiffel Tower', 'Champ de Mars, 5 Avenue Anatole France, Paris', '75007', 4.6, 18000, 'France')
ON CONFLICT DO NOTHING;

-- For existing databases, run these ALTER TABLE statements:
-- ALTER TABLE places ADD COLUMN IF NOT EXISTS rating FLOAT4 DEFAULT 0.0;
-- ALTER TABLE places ADD COLUMN IF NOT EXISTS followers FLOAT4 DEFAULT 0.0;
-- ALTER TABLE places ADD COLUMN IF NOT EXISTS country VARCHAR(100) DEFAULT 'Unknown';

-- Add pincode validation constraint if not exists
-- ALTER TABLE places ADD CONSTRAINT IF NOT EXISTS check_pincode_format CHECK (length(pincode) < 10 AND pincode ~ '^[0-9]+$');

-- Update existing pincodes to ensure they are less than 10 characters
UPDATE places 
SET pincode = format_pincode(pincode)
WHERE pincode IS NOT NULL;

-- Verify the changes
SELECT 
    id, 
    name, 
    pincode,
    length(pincode) as pincode_length,
    validate_pincode(pincode) as is_valid_pincode
FROM places 
ORDER BY id
LIMIT 10;
