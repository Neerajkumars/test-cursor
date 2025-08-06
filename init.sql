-- Initialize the dynamic_api_db database
-- This script runs when PostgreSQL container starts for the first time

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Set timezone
SET timezone = 'UTC';

-- Create a schema for dynamic tables (optional)
CREATE SCHEMA IF NOT EXISTS dynamic_apis;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE dynamic_api_db TO "user";
GRANT ALL PRIVILEGES ON SCHEMA public TO "user";
GRANT ALL PRIVILEGES ON SCHEMA dynamic_apis TO "user";