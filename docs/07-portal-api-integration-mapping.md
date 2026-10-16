# MedFlow Portal–API Integration Mapping

**Status:** Proposed design — not implemented or integration-tested
**Scope:** Local browser portal prototype and local claims API
**Architecture reference:** `docs/MedFlow.md`
**Related artifacts:** `medflow-portal-prototype/`, `medflow-local-api/`, `medflow-api-contract/`, and [`CONTRACT-CONFORMANCE-REVIEW.md`](../CONTRACT-CONFORMANCE-REVIEW.md), documenting local mock alignment and known gaps.

## 1. Purpose and current state

This document records the field mappings, behavioral differences, and security boundaries that must be addressed before the MedFlow portal prototype can be integrated with the local claims API.

The portal prototype and local API are currently separate implementations:

- The portal is a browser-only prototype that stores synthetic claim records in `localStorage` and simulates processing.
- The local API exposes claim submission, listing, detail, and health endpoints. Its data is in memory, and processing is simulated.
- The proposed OpenAPI contract describes a future API with authentication and additional production-oriented requirements. It is not evidence of a deployed or conformant service.
- The AWS architecture in `docs/MedFlow.md` is the intended architectural reference, not proof that all production components have been implemented.

**No integration is claimed by this document.**

## 2. Field mapping

| Concept | Portal prototype | Local API | Integration decision |
|---|---|---|---|
| Client reference | `clientRef` | `clientReference` | Map explicitly and validate against the API's rules. |
| Service date | `serviceDate` | `serviceDate` | Preserve the date representation and validate before submission. |
| Amount | JavaScript numeric value; UI presents USD | JSON numeric `amount` | Confirm currency and precision rules; do not rely on display formatting for validation. |
| Document name | Selected filename | `document.fileName` | Send metadata only when the API schema permits it. |
| Document content type | Browser file metadata may be available | `document.contentType` | Validate the value and type before submission. |
| Document size | Browser file metadata may be available | `document.sizeBytes` | Treat as metadata, not proof that file bytes were uploaded or inspected. |
| Claim identifier | Prototype-local record identifier | API-generated `claimId` | Use the API identifier after successful submission. |
| Claim status | Human-readable labels | `PROCESSING`, `ACCEPTED`, `MANUAL_REVIEW`, `REJECTED` | Map API enum values to display labels in the UI. |
| Idempotency | Prototype-generated local key | `Idempotency-Key` request header | Generate and retain a submission key across retries of the same logical request. |
| Tenant/workspace | Browser-selected workspace | `X-Demo-Tenant` in the local mock | Neither value is authenticated tenant identity. |
| Status URL | No demonstrated API integration | `statusUrl` in accepted response | Use the returned URL or documented claim endpoint when implementing status polling. |

Check this mapping against current source code and schemas before implementation. It is a design guide, not a substitute for runtime verification.

## 3. Proposed request and response flow

1. The portal validates the form locally for user experience.
2. The portal constructs a request using the API's field names and documented schema.
3. The portal sends the request to the configured API origin, including the idempotency header.
4. The API validates the request and returns either a structured error or an accepted response.
5. The portal stores the returned API claim identifier and status rather than inventing an independent server-side result.
6. The portal retrieves claim status from the API and renders the API's current status.
7. The UI distinguishes network failures, validation errors, authorization failures, conflicts, and processing states. It must not silently replace server errors with simulated success.

The prototype's timer-based processing behavior must be removed or isolated from the integrated path so that it cannot contradict API state.

## 4. Status mapping

| API status | Suggested display label |
|---|---|
| `PROCESSING` | Processing |
| `ACCEPTED` | Accepted |
| `MANUAL_REVIEW` | Manual review |
| `REJECTED` | Rejected |

These are display mappings only. The UI must not infer a terminal status merely because a timer expires. Unknown status values should be handled safely rather than treated as success.

## 5. Security boundaries

The existing prototype is not an authenticated multi-tenant portal.

- Browser `localStorage` is client-controlled and is not an authoritative claims database.
- A workspace selector is a UI feature, not tenant authorization.
- `X-Demo-Tenant` is suitable only for the current local mock; it must not be trusted as the identity source for a production tenant.
- The intended architecture describes Cognito-based user authentication, validated tenant identity, and tenant filtering at the data-access layer.
- Production integration must enforce authorization on the server for list, detail, submission, and status operations.
- Tenant A must not be able to read or alter Tenant B's claims by changing browser state, request headers, claim IDs, or URLs.
- Sensitive claim responses must not be stored in shared caches. Responses containing tenant-specific data should use appropriate cache controls.
- CORS configuration is not authentication or authorization.

Do not use real medical documents or sensitive personal information in the local demonstration.

## 6. Idempotency and duplicate submissions

The portal should retain the same idempotency key when retrying the same logical request after an ambiguous network failure. A new logical submission should receive a new key.

Before production readiness can be claimed, tests must establish:

- Repeating an equivalent request with the same key does not create a second logical claim.
- Reusing the key with a materially different request returns the documented conflict behavior.
- Duplicate client references follow the documented API policy.
- Idempotency survives API process restarts and concurrent requests.

The current local API's in-memory behavior is a learning implementation and does not establish durable production idempotency.

## 7. Document handling

The current portal prototype records a selected filename; the local API accepts document metadata. Neither behavior demonstrates actual document upload, malware scanning, OCR, or durable storage.

A future upload design must define the upload mechanism, size limits, allowed content types, content verification, malware scanning, storage permissions, retention, and failure handling. Metadata must never be represented as proof that document bytes were received or scanned.

## 8. Contract and error handling

The proposed OpenAPI contract and the local API must be reconciled before claiming contract conformance.

The implementation review must explicitly address authentication and authorization, tenant isolation, request and response schemas, pagination, status URLs, idempotency, cache controls, and error behavior. The local mock does not currently demonstrate all proposed authentication, throttling, and error-response requirements.

Contract parser validation and automated request/response conformance testing remain separate verification tasks.

## 9. Acceptance criteria

Integration should not be marked complete until evidence demonstrates all of the following:

- [ ] The portal submits a claim to the local API rather than simulating acceptance.
- [ ] Field names, validation, numeric amounts, dates, and document metadata match the agreed schema.
- [ ] The portal uses the API-generated claim ID and displays status retrieved from the API.
- [ ] Network failures and structured API errors are shown accurately.
- [ ] Repeated submissions and retry behavior follow the agreed idempotency policy.
- [ ] List and detail responses are handled correctly, including pagination.
- [ ] Tenant isolation is tested against the server's authorization boundary.
- [ ] No sensitive claim data is exposed through browser storage or inappropriate caching.
- [ ] Contract validation and automated conformance tests pass.
- [ ] The README documents how to run the integrated demo and clearly states its remaining limitations.

## 10. Evidence and reporting

Record test commands, results, timestamps, and relevant sanitized outputs. Distinguish clearly between:

- **Implemented:** code exists.
- **Tested locally:** the stated test ran and passed.
- **Contract-validated:** implementation was checked against the agreed contract.
- **AWS-validated:** the behavior was exercised in AWS with evidence.
- **Production-ready:** all applicable security, reliability, operational, and acceptance requirements have been demonstrated.

Passing local unit tests alone does not establish AWS deployment, production tenant isolation, durable persistence, or production readiness.

## 11. Decision

Keep the portal prototype, local API, and proposed OpenAPI contract as distinct artifacts until an explicit integration change is implemented and verified. The local API is the candidate source of truth for the local demonstration; the proposed contract and AWS architecture remain separate design references until reconciled with implementation evidence.