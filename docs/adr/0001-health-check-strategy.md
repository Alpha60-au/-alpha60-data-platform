# ADR-0001: Health Check Strategy

- **Status:** Proposed
- **Date:** 2026-07-03

## Context

As ALPHA60 transitions from a development project to a production data platform, operators require a consistent way to verify that external dependencies are correctly configured and reachable before ingestion jobs are executed.

Health checks should provide confidence that the platform is operational without modifying business data.

## Decision

The platform will expose health checks through the CLI.

```text
alpha60 test config
alpha60 test shopify
alpha60 test bigquery
alpha60 test all
```

### Configuration Check

Verifies that all required configuration has been supplied.

Examples include:

- Shopify store domain
- Shopify access token
- BigQuery project
- BigQuery dataset
- Required environment variables

No external services are contacted.

### Shopify Check

Verifies:

- Configuration is valid.
- Authentication succeeds.
- Shopify API is reachable.

The check must perform a read-only operation.

No data should be modified.

### BigQuery Check

Verifies:

- Configuration is valid.
- Authentication succeeds.
- Target dataset is accessible.

The check must not create, modify, or delete tables.

### Full Platform Check

Runs every configured health check and returns a combined result.

## Consequences

Benefits:

- Safe to execute before deployments.
- Safe to execute from CI/CD.
- Safe to execute on Cloud Run startup.
- Safe for operational troubleshooting.

Health checks are intentionally independent from ingestion jobs.

A successful health check does **not** guarantee that an ingestion job will succeed, but it provides confidence that the platform can communicate with its required external dependencies.

## Future Considerations

Future versions may include:

- Secret Manager validation
- Scheduler validation
- Cloud Run readiness
- Network connectivity diagnostics
- Warehouse write permission validation using temporary resources