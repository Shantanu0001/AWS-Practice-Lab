# API contract acceptance checklist

Use synthetic data only. These checks are requirements for the future backend, not results already observed.

## Functional
- [ ] `GET /v1/claims` returns only records in the authenticated tenant scope.
- [ ] `GET /v1/claims?status=PROCESSING` filters valid status values.
- [ ] Invalid status, limit, and pagination tokens receive a safe `400`.
- [ ] `POST /v1/claims` validates required fields, date format, amount range, and unknown fields.
- [ ] A valid submit returns `202`, a claim ID, and `PROCESSING` before async work finishes.
- [ ] `GET /v1/claims/{claimId}` reflects eventual status changes.
- [ ] All tenant-specific responses include `Cache-Control: no-store`.

## Authentication and tenant isolation — release blockers
- [ ] Missing, expired, malformed, or wrong-issuer token is rejected.
- [ ] Tenant context comes from verified server-side identity context, not a body/query/header value chosen by the browser.
- [ ] Tenant A cannot list Tenant B's claims.
- [ ] Tenant A cannot retrieve Tenant B's claim by guessing its ID; response does not reveal whether another tenant owns that ID.
- [ ] Database queries include tenant scope even after authorization middleware passes.
- [ ] CloudFront/API cache configuration cannot replay one tenant's response to another tenant.

## Idempotency and retry safety
- [ ] Same tenant + same `Idempotency-Key` + same normalized request produces one logical claim and a stable response.
- [ ] Same tenant + same key + different request payload returns `409`.
- [ ] Same key used by a different tenant does not expose or collide with another tenant's record.
- [ ] Concurrent duplicate submissions still create only one logical claim.
- [ ] The downstream queue consumer can process duplicate delivery without duplicating claim effects.

## Error handling and operations
- [ ] Error response contains stable `code`, safe `message`, and `requestId`.
- [ ] No error response contains stack traces, secret values, raw document content, or other-tenant data.
- [ ] Rate limiting returns `429` and a useful `Retry-After` where configured.
- [ ] Logs correlate requests without logging bearer tokens or sensitive document contents.
- [ ] API schema validation is enforced at the edge and repeated in application logic.
