-- SIH26093 Database Initialization Script
-- This is a placeholder. The actual schema is created by SQLAlchemy via Alembic.
-- When the backend starts, the database tables are created automatically based on the models.

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create database (if running manually)
-- CREATE DATABASE nhaa_triage;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE nhaa_triage TO nhaa_user;

-- Note: All tables are created via SQLAlchemy/Alembic migrations.
-- See: backend/app/models/ for model definitions.

-- Optional: Insert seed data for demo mode
-- This will be handled by the application on first startup in DEMO mode.
