# ALPHA60 Data Platform Architecture

This document is the living architecture reference for the ALPHA60 Data Platform.

## Current Version

**v0.3.0**

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

### CLI

- `alpha60 ingest shopify-products`

## Phase 2 Objectives

1. Operational health checks
2. Structured logging and observability
3. Incremental loading
4. Cloud Run deployment
5. GitHub Actions CI/CD
6. Scheduling
7. Secrets management
8. Production hardening

## Documentation

- `architecture.md` — Living architecture
- `adr/` — Architecture Decision Records