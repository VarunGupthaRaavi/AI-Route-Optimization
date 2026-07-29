-- ===================================================================
-- ROUTEAI SUPABASE SCHEMA COLUMN ALIGNMENT SCRIPT
-- Run this in Supabase SQL Editor to fix 'column notes does not exist' and all missing columns
-- ===================================================================

-- 1. Rename password_hash column to hashed_password on public.users
DO $$ 
BEGIN 
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='password_hash') THEN
        ALTER TABLE public.users RENAME COLUMN password_hash TO hashed_password;
    END IF;
END $$;

-- 2. Users Table Columns
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS hashed_password VARCHAR(255);
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMPTZ;
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

-- 3. Customers Table Columns
ALTER TABLE public.customers ADD COLUMN IF NOT EXISTS notes TEXT;
ALTER TABLE public.customers ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;
ALTER TABLE public.customers ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

-- 4. Vehicles Table Columns
ALTER TABLE public.vehicles ADD COLUMN IF NOT EXISTS max_range_km DOUBLE PRECISION DEFAULT 500.0;
ALTER TABLE public.vehicles ADD COLUMN IF NOT EXISTS current_lat DOUBLE PRECISION;
ALTER TABLE public.vehicles ADD COLUMN IF NOT EXISTS current_lng DOUBLE PRECISION;
ALTER TABLE public.vehicles ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;
ALTER TABLE public.vehicles ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

-- 5. Drivers Table Columns
ALTER TABLE public.drivers ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES public.users(id) ON DELETE SET NULL;
ALTER TABLE public.drivers ADD COLUMN IF NOT EXISTS current_lat DOUBLE PRECISION;
ALTER TABLE public.drivers ADD COLUMN IF NOT EXISTS current_lng DOUBLE PRECISION;
ALTER TABLE public.drivers ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;
ALTER TABLE public.drivers ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

-- 6. Deliveries Table Columns
ALTER TABLE public.deliveries ADD COLUMN IF NOT EXISTS scheduled_date TIMESTAMPTZ;
ALTER TABLE public.deliveries ADD COLUMN IF NOT EXISTS delivered_at TIMESTAMPTZ;
ALTER TABLE public.deliveries ADD COLUMN IF NOT EXISTS notes TEXT;
ALTER TABLE public.deliveries ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;
ALTER TABLE public.deliveries ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

-- 7. Routes Table Columns
ALTER TABLE public.routes ADD COLUMN IF NOT EXISTS total_deliveries INT DEFAULT 0;
ALTER TABLE public.routes ADD COLUMN IF NOT EXISTS started_at TIMESTAMPTZ;
ALTER TABLE public.routes ADD COLUMN IF NOT EXISTS completed_at TIMESTAMPTZ;
ALTER TABLE public.routes ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;
ALTER TABLE public.routes ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

-- 8. Route Stops Table Columns
ALTER TABLE public.route_stops ADD COLUMN IF NOT EXISTS estimated_arrival TIMESTAMPTZ;
ALTER TABLE public.route_stops ADD COLUMN IF NOT EXISTS completed BOOLEAN DEFAULT FALSE;
ALTER TABLE public.route_stops ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;
ALTER TABLE public.route_stops ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

-- 9. Notifications & RAG Tables
ALTER TABLE public.notifications ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;
ALTER TABLE public.notifications ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

ALTER TABLE public.knowledge_documents ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;
ALTER TABLE public.knowledge_documents ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

ALTER TABLE public.knowledge_chunks ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;
ALTER TABLE public.knowledge_chunks ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

-- 10. Re-seed Admin User with valid bcrypt hash for admin123
INSERT INTO public.users (id, email, hashed_password, full_name, role, is_active, is_verified, is_deleted)
VALUES (
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'admin@routeai.com',
    '$2b$12$C66IAyilIWN9WUIf3R5O0.8Fam0x7DEiwfzyePXDlyRs.pJ2t8uAC',
    'System Administrator',
    'ADMIN',
    true,
    true,
    false
) ON CONFLICT (email) DO UPDATE 
SET hashed_password = '$2b$12$C66IAyilIWN9WUIf3R5O0.8Fam0x7DEiwfzyePXDlyRs.pJ2t8uAC',
    is_active = true;
