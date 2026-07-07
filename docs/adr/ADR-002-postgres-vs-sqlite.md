# ADR-002: PostgreSQL over SQLite
PostgreSQL chosen for realistic parity with production deployment
(cloud Postgres via Supabase/Neon in Phase 6) and proper concurrent
write support, over SQLite's single-writer limitation.