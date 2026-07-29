-- ===================================================================
-- ROUTEAI SUPABASE CLOUD POSTGRESQL MIGRATION 001_INITIAL_SCHEMA.SQL
-- Contains Table Creation DDL, RLS Policies, & Production Seed Data
-- ===================================================================

-- 1. Enable Required PostgreSQL Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ===================================================================
-- 2. CREATE SCHEMA TABLES
-- ===================================================================

-- Users Table
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'CUSTOMER',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    last_login_at TIMESTAMPTZ,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Customers Table
CREATE TABLE IF NOT EXISTS public.customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    company_name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Vehicles Table
CREATE TABLE IF NOT EXISTS public.vehicles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    license_plate VARCHAR(50) UNIQUE NOT NULL,
    vehicle_model VARCHAR(255) NOT NULL,
    capacity_kg DOUBLE PRECISION NOT NULL,
    volume_m3 DOUBLE PRECISION NOT NULL,
    fuel_type VARCHAR(50) NOT NULL DEFAULT 'DIESEL',
    status VARCHAR(50) NOT NULL DEFAULT 'IDLE',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Drivers Table
CREATE TABLE IF NOT EXISTS public.drivers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    license_number VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(50) NOT NULL,
    assigned_vehicle_id UUID REFERENCES public.vehicles(id) ON DELETE SET NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'AVAILABLE',
    rating DOUBLE PRECISION DEFAULT 5.0,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Deliveries Table
CREATE TABLE IF NOT EXISTS public.deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tracking_number VARCHAR(100) UNIQUE NOT NULL,
    customer_id UUID REFERENCES public.customers(id) ON DELETE CASCADE,
    pickup_address TEXT NOT NULL,
    delivery_address TEXT NOT NULL,
    pickup_lat DOUBLE PRECISION,
    pickup_lng DOUBLE PRECISION,
    delivery_lat DOUBLE PRECISION,
    delivery_lng DOUBLE PRECISION,
    weight_kg DOUBLE PRECISION NOT NULL,
    volume_m3 DOUBLE PRECISION NOT NULL,
    priority VARCHAR(50) NOT NULL DEFAULT 'MEDIUM',
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Routes Table
CREATE TABLE IF NOT EXISTS public.routes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    route_code VARCHAR(100) UNIQUE NOT NULL,
    driver_id UUID REFERENCES public.drivers(id) ON DELETE SET NULL,
    vehicle_id UUID REFERENCES public.vehicles(id) ON DELETE SET NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'PLANNED',
    total_distance_km DOUBLE PRECISION DEFAULT 0.0,
    estimated_duration_minutes DOUBLE PRECISION DEFAULT 0.0,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Route Stops Table
CREATE TABLE IF NOT EXISTS public.route_stops (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    route_id UUID REFERENCES public.routes(id) ON DELETE CASCADE,
    delivery_id UUID REFERENCES public.deliveries(id) ON DELETE CASCADE,
    stop_sequence INT NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Notifications Table
CREATE TABLE IF NOT EXISTS public.notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(50) NOT NULL DEFAULT 'INFO',
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Knowledge Documents Table (Enterprise RAG)
CREATE TABLE IF NOT EXISTS public.knowledge_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) DEFAULT 'pdf',
    author VARCHAR(255) DEFAULT 'System',
    chunk_count INT DEFAULT 0,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Knowledge Chunks Table (Vector Store)
CREATE TABLE IF NOT EXISTS public.knowledge_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES public.knowledge_documents(id) ON DELETE CASCADE,
    chunk_index INT NOT NULL,
    content TEXT NOT NULL,
    embedding_vector JSONB,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Ensure column names are aligned if table already exists
DO $$ 
BEGIN 
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='password_hash') THEN
        ALTER TABLE public.users RENAME COLUMN password_hash TO hashed_password;
    END IF;
END $$;

ALTER TABLE public.users ADD COLUMN IF NOT EXISTS hashed_password VARCHAR(255);
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMPTZ;
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE, ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
ALTER TABLE public.customers ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE, ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
ALTER TABLE public.vehicles ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE, ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
ALTER TABLE public.drivers ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE, ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
ALTER TABLE public.deliveries ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE, ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
ALTER TABLE public.routes ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE, ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
ALTER TABLE public.route_stops ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE, ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
ALTER TABLE public.notifications ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE, ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
ALTER TABLE public.knowledge_documents ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE, ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
ALTER TABLE public.knowledge_chunks ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE, ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

-- ===================================================================
-- 3. ROW LEVEL SECURITY (RLS) POLICIES
-- ===================================================================

ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.vehicles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.drivers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.deliveries ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.routes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.route_stops ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.knowledge_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.knowledge_chunks ENABLE ROW LEVEL SECURITY;

-- Allow Service Role and Authenticated Application Users Full Access
CREATE POLICY "Allow service role full access to users" ON public.users FOR ALL USING (true);
CREATE POLICY "Allow service role full access to customers" ON public.customers FOR ALL USING (true);
CREATE POLICY "Allow service role full access to vehicles" ON public.vehicles FOR ALL USING (true);
CREATE POLICY "Allow service role full access to drivers" ON public.drivers FOR ALL USING (true);
CREATE POLICY "Allow service role full access to deliveries" ON public.deliveries FOR ALL USING (true);
CREATE POLICY "Allow service role full access to routes" ON public.routes FOR ALL USING (true);
CREATE POLICY "Allow service role full access to route_stops" ON public.route_stops FOR ALL USING (true);
CREATE POLICY "Allow service role full access to notifications" ON public.notifications FOR ALL USING (true);
CREATE POLICY "Allow service role full access to knowledge_documents" ON public.knowledge_documents FOR ALL USING (true);
CREATE POLICY "Allow service role full access to knowledge_chunks" ON public.knowledge_chunks FOR ALL USING (true);

-- ===================================================================
-- 4. SEED INITIAL DATA
-- ===================================================================

-- Default Admin User (Password: admin123 -> bcrypt hash)
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
) ON CONFLICT (email) DO NOTHING;

-- Initial Customers
INSERT INTO public.customers (id, name, company_name, email, phone, address, latitude, longitude, is_deleted)
VALUES 
(
    '11111111-1111-4111-a111-111111111111',
    'Acme Global Corp',
    'Acme Logistics',
    'contact@acme.com',
    '+1-555-0192',
    '742 Evergreen Terrace, Springfield',
    37.7749,
    -122.4194,
    false
),
(
    '22222222-2222-4222-a222-222222222222',
    'Apex Retailers Ltd',
    'Apex Supply',
    'info@apexretail.com',
    '+1-555-0183',
    '100 Market St, San Francisco, CA',
    37.7893,
    -122.4014,
    false
) ON CONFLICT (id) DO NOTHING;

-- Initial Vehicles
INSERT INTO public.vehicles (id, license_plate, vehicle_model, capacity_kg, volume_m3, fuel_type, status, is_deleted)
VALUES 
(
    '33333333-3333-4333-a333-333333333333',
    'TRK-9082',
    'Volvo FH16 Heavy Duty',
    15000.0,
    45.0,
    'DIESEL',
    'AVAILABLE',
    false
),
(
    '44444444-4444-4444-a444-444444444444',
    'VAN-4091',
    'Mercedes-Benz Sprinter EV',
    3500.0,
    14.0,
    'ELECTRIC',
    'IDLE',
    false
) ON CONFLICT (license_plate) DO NOTHING;

-- Initial Drivers
INSERT INTO public.drivers (id, license_number, phone, assigned_vehicle_id, status, rating, is_deleted)
VALUES 
(
    '55555555-5555-4555-a555-555555555555',
    'DL-US-982104',
    '+1-555-8831',
    '33333333-3333-4333-a333-333333333333',
    'AVAILABLE',
    4.95,
    false
) ON CONFLICT (license_number) DO NOTHING;
