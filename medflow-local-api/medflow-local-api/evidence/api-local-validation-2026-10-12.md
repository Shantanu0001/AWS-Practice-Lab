# Local MedFlow API Validation Evidence

**Date:** 2026-10-12
**Scope:** Local in-memory mock only; no AWS deployment was performed for these tests.

## Automated suite

Command:

`python -B -m unittest discover -s tests -v`

Observed result: **22 tests passed; exit code 0; runtime 0.573 seconds.**

Coverage represented in the passing suite includes:
- Health endpoint and no-store headers
- Tenant-scoped listing and hidden cross-tenant detail
- Pagination and tenant-bound tokens
- Submission validation for idempotency keys, client references, dates, amounts, document metadata, and unknown fields
- Idempotency replay, equivalent amount formats, and conflicting payloads
- Flat error response shape

## Targeted concurrency and tenant-key checks

Observed result: **PASS**

- Eight concurrent same-tenant submissions using the same key and payload all returned HTTP 202 and the same claim ID (`CLM-3001`).
- Two demo tenants using the same idempotency key with the same payload received distinct claim IDs (`CLM-3002` and `CLM-3003`).

These targeted checks ran against one local server process with in-memory state.

## Contract example alignment

The list-response example previously included `"nextToken": null`, while the OpenAPI schema declares `nextToken` as an optional string without allowing null. The no-next-page example was changed to omit the property. The original file was backed up before modification.

## Limitations and outstanding production requirements

- `X-Demo-Tenant` is a local demo selector, not verified authentication.
- These tests do not establish cross-process or distributed idempotency.
- Durable persistence, real queue/Step Functions processing, JWT validation, rate limiting, and production cache configuration were not verified by these tests.
- The proposed API contract is not a deployed service.
- Stage 3 infrastructure acceptance criteria are separate from this local API evidence.
