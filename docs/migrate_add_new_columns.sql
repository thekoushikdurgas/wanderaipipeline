-- Migration script to add new columns to existing places table
-- Run this script in your database to add the new columns

-- Add new columns if they don't exist
ALTER TABLE places ADD COLUMN IF NOT EXISTS rating FLOAT4 DEFAULT 0.0;
ALTER TABLE places ADD COLUMN IF NOT EXISTS followers FLOAT4 DEFAULT 0.0;
ALTER TABLE places ADD COLUMN IF NOT EXISTS country VARCHAR(100) DEFAULT 'Unknown';
ALTER TABLE places ADD COLUMN IF NOT EXISTS description TEXT DEFAULT '';

-- Create indexes for better performance on new columns
CREATE INDEX IF NOT EXISTS idx_places_rating ON places(rating);
CREATE INDEX IF NOT EXISTS idx_places_country ON places(country);
CREATE INDEX IF NOT EXISTS idx_places_description ON places(description);

-- Update existing records to have default values
UPDATE places SET 
    rating = 0.0 WHERE rating IS NULL;
UPDATE places SET 
    followers = 0.0 WHERE followers IS NULL;
UPDATE places SET 
    country = 'Unknown' WHERE country IS NULL OR country = '';
UPDATE places SET 
    description = '' WHERE description IS NULL;

-- Drop existing pincode constraint if it exists (to avoid conflicts)
ALTER TABLE places DROP CONSTRAINT IF EXISTS check_pincode_format;
ALTER TABLE places DROP CONSTRAINT IF EXISTS places_pincode_check;

-- Add pincode validation constraint (flexible 6-character format)
ALTER TABLE places ADD CONSTRAINT check_pincode_format CHECK (length(pincode) = 6);

-- Function to validate pincode format (supports both numeric and alphanumeric)
CREATE OR REPLACE FUNCTION validate_pincode(pincode_input TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    -- Check if pincode is exactly 6 characters (digits or alphanumeric)
    IF length(pincode_input) = 6 THEN
        RETURN TRUE;
    ELSE
        RETURN FALSE;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Function to format pincode (add leading zeros for numeric pincodes)
CREATE OR REPLACE FUNCTION format_pincode(pincode_input TEXT)
RETURNS TEXT AS $$
BEGIN
    -- Remove any spaces and convert to uppercase
    pincode_input := trim(upper(pincode_input));
    
    -- If it's numeric and less than 6 digits, pad with leading zeros
    IF pincode_input ~ '^[0-9]+$' AND length(pincode_input) < 6 THEN
        RETURN lpad(pincode_input, 6, '0');
    END IF;
    
    -- If it's exactly 6 characters, return as is
    IF length(pincode_input) = 6 THEN
        RETURN pincode_input;
    END IF;
    
    -- If it's longer than 6 characters, truncate
    IF length(pincode_input) > 6 THEN
        RETURN substring(pincode_input from 1 for 6);
    END IF;
    
    -- Default case: return as is
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
        RAISE EXCEPTION 'Invalid pincode format. Must be exactly 6 characters.';
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

-- Update existing pincodes to ensure they are exactly 6 characters
UPDATE places 
SET pincode = format_pincode(pincode)
WHERE pincode IS NOT NULL;

-- Verify the changes
SELECT 
    id, 
    name, 
    pincode,
    length(pincode) as pincode_length,
    validate_pincode(pincode) as is_valid_pincode,
    rating,
    followers,
    country,
    description
FROM places 
ORDER BY id
LIMIT 10;
