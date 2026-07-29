-- ===================================================================
-- ROUTEAI SUPABASE SCHEMA COLUMN ALIGNMENT SCRIPT
-- Run this in Supabase SQL Editor to fix 'column users.hashed_password does not exist'
-- ===================================================================

-- 1. Rename password_hash column to hashed_password on public.users
DO $$ 
BEGIN 
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='password_hash') THEN
        ALTER TABLE public.users RENAME COLUMN password_hash TO hashed_password;
    END IF;
END $$;

-- 2. Add missing user columns
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS hashed_password VARCHAR(255);
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMPTZ;
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

-- 3. Add missing soft-delete columns across all logistics tables
ALTER TABLE public.customers ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE, ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
ALTER TABLE public.vehicles ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE, ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
ALTER TABLE public.drivers ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE, ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
ALTER TABLE public.deliveries ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE, ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
ALTER TABLE public.routes ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE, ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
ALTER TABLE public.route_stops ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE, ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
ALTER TABLE public.notifications ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE, ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
ALTER TABLE public.knowledge_documents ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE, ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
ALTER TABLE public.knowledge_chunks ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE, ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

-- 4. Re-seed Admin User with valid bcrypt hash for admin123
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
