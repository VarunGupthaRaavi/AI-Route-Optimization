/**
 * RouteAI Supabase Cloud PostgreSQL Migration Runner (Node.js)
 * Executes 001_initial_schema.sql against Supabase PostgreSQL using pg / postgres connection pool.
 */

const fs = require('fs');
const path = require('path');
const { Client } = require('pg');

async function runMigrations() {
  console.log('🚀 RouteAI Supabase Node Migration Runner');

  // Read SQL migration file
  const migrationPath = path.join(__dirname, 'migrations', '001_initial_schema.sql');
  if (!fs.existsSync(migrationPath)) {
    console.error(`❌ Migration file not found at: ${migrationPath}`);
    process.exit(1);
  }

  const sql = fs.readFileSync(migrationPath, 'utf8');

  // Get Database URL from environment or prompt
  const dbUrl = process.env.DATABASE_URL || process.env.SUPABASE_DATABASE_URL;

  if (!dbUrl) {
    console.error('❌ Error: DATABASE_URL environment variable is required.');
    console.log('Usage: DATABASE_URL="postgres://..." node supabase/apply_migrations.js');
    process.exit(1);
  }

  // Format connection string for pg driver
  const connectionString = dbUrl.replace('postgresql+asyncpg://', 'postgres://');

  const client = new Client({
    connectionString,
    ssl: { rejectUnauthorized: false }
  });

  try {
    console.log('📡 Connecting to Supabase Managed PostgreSQL database...');
    await client.connect();

    console.log('📜 Executing migration script: 001_initial_schema.sql...');
    await client.query(sql);

    console.log('✅ Migration executed successfully!');

    // Query list of created tables
    const res = await client.query(
      "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
    );
    const tables = res.rows.map(r => r.table_name);
    console.log(`📊 Verified ${tables.length} tables in Supabase public schema:`, tables.join(', '));

  } catch (err) {
    console.error('❌ Migration Error:', err.message);
    process.exit(1);
  } finally {
    await client.end();
  }
}

runMigrations();
