# MedFlow Claims API Contract — draft v0.1

This is the next implementation artifact for the local MedFlow portal prototype. It defines a small proposed contract for listing claims, submitting claim metadata, and reading a claim's status.

**Status:** proposed, not deployed, and not yet reconciled with a running backend. The project source establishes Cognito/JWT tenant context, server-side tenant scoping, asynchronous processing, idempotency, and no-cache behavior for tenant-specific claim responses. The exact endpoint paths and schema below are a practical proposal to review before implementation.

## Included
- `openapi/medflow-claims-v1.yaml`: OpenAPI 3.0.3 contract
- `examples/list-claims-response.json`: list response
- `examples/submit-claim-request.json`: submission request
- `examples/submit-claim-accepted.json`: asynchronous acceptance response
- `examples/get-claim-response.json`: status response
- `tests/acceptance-checklist.md`: behavioral and security checks before backend integration

## Proposed routes

| Method | Route | Purpose |
|---|---|---|
| GET | `/v1/claims` | List claims in caller's tenant scope |
| POST | `/v1/claims` | Accept metadata and enqueue processing |
| GET | `/v1/claims/{claimId}` | Get claim detail/status in caller's tenant scope |

## Contract decisions to preserve

1. **Tenant identity is not a request field.** The server derives tenant context from a verified identity/token context. Do not accept `tenantId` from the browser as authority.
2. **Defense in depth.** Every data access is scoped by both the requested record and the authenticated tenant. A claim ID alone is not authorization.
3. **Asynchronous submit.** Return `202 Accepted` with a claim ID and `PROCESSING`; do not make the browser wait for the full pipeline.
4. **Idempotency.** `Idempotency-Key` is required for submit. The server must persist the key within tenant scope and return a consistent result for a same-key/same-payload retry. A same-key/conflicting-payload request should be rejected.
5. **No shared caching of tenant data.** Responses for list/detail/submit use `Cache-Control: no-store`; the CloudFront API behavior must not cache them.
6. **Safe errors.** Return a request/correlation ID, stable error code, and user-safe message. Do not leak stack traces, internal IDs, secrets, or another tenant's data.
7. **Document upload is not implemented in this contract yet.** The optional `document` field describes metadata only. A later upload design should authorize uploads and validate file size/type/content server-side.

## Validate locally

The YAML is a specification file, not a deployed service. You can review it with an OpenAPI-compatible editor or validator. No AWS deployment is required. The `.invalid` server URL is deliberately a placeholder and must not be called.
