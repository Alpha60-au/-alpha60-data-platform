# ALPHA60 Data Platform Architecture

This document is the living architecture reference for the ALPHA60 Data Platform.

## Current Version

**v0.4.x**

## Platform Goals

The platform is designed to:

- Extract operational data from business systems.
- Standardise and validate data.
- Load data into BigQuery.
- Provide a reliable foundation for reporting, analytics and future automation.

## Architectural Principles

- Clean Architecture
- Strong typing
- Provider-based design
- Dependency injection via composition root
- Test-first implementation
- Small, reviewable commits
- No hidden framework magic
- Production-first engineering

## Current Components

### Configuration

- Provider-aware settings
- Environment-based configuration

### Connectors

- Shopify

### Warehouse

- BigQuery

### Jobs

- Shopify Products ingestion

### Operations

- Health check framework
- Structured JSON logging
- Incremental state model
- BigQuery-backed operational metadata repository foundation

### CLI

- `alpha60 ingest shopify-products`
- `alpha60 test config`
- `alpha60 test shopify`
- `alpha60 test bigquery`
- `alpha60 test all`

## Operations Metadata

Operational metadata is stored in BigQuery so that state survives Cloud Run container restarts and remains queryable for audit, monitoring and reporting.

### `platform_state`

Stores the current resumable state for operational processes.

This table answers:

> Where should this job resume from?

Expected columns:

| Column | Type | Purpose |
| --- | --- | --- |
| `job_name` | STRING | Unique job identifier |
| `cursor_field` | STRING | Source field used for incremental loading |
| `cursor_value` | TIMESTAMP | Last successfully processed cursor value |
| `updated_at` | TIMESTAMP | Time the state was last updated |

Design rules:

- One row per job.
- Mutable current state only.
- Used by ingestion jobs before and after successful runs.

### `job_history`

Stores an append-only record of job executions.

This table answers:

> What happened over time?

Expected columns:

| Column | Type | Purpose |
| --- | --- | --- |
| `job_name` | STRING | Unique job identifier |
| `run_started_at` | TIMESTAMP | Job start time |
| `run_completed_at` | TIMESTAMP | Job completion time |
| `status` | STRING | Job result |
| `rows_processed` | INTEGER | Number of rows processed |
| `duration_seconds` | FLOAT | Runtime duration |
| `message` | STRING | Human-readable execution summary |

Design rules:

- Append-only.
- No current-state responsibility.
- Used for audit, dashboards and operational monitoring.

## Phase 3 Objectives

1. Structured logging
2. Incremental loading
3. Cloud Run deployment
4. GitHub Actions CI/CD
5. Secret Manager integration
6. Cloud Scheduler
7. Production hardening
8. v1.0.0 release

## Documentation

- `architecture.md` — Living architecture
- `adr/` — Architecture Decision Records