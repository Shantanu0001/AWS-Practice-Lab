# MedFlow API contract conformance review - updated local mock

This review applies to the proposed OpenAPI contract in `medflow-api-contract/medflow-api-contract/openapi/medflow-claims-v1.yaml`. The local server remains a learning mock, not a deployed or production-secure API.

## Aligned in this revision
- Enforces Idempotency-Key length 8-128.
- Enforces clientReference length/pattern, serviceDate format, amount range/cent precision.
- Accepts optional `document` metadata with `fileName`, `contentType`, and `sizeBytes`; raw bytes are not uploaded.
- Returns `202` body with `claimId`, `status`, `acceptedAt`, and `statusUrl`.
- Returns flat error objects: `code`, `message`, `requestId`.
- Returns claim details directly and lists as `{items, nextToken?}`.
- Implements opaque, tenant-bound offset pagination for local demonstration.
- Adds `updatedAt` to claims and `Cache-Control: no-store` on API responses.

## Explicit boundaries / remaining gaps
- `X-Demo-Tenant` is client-controlled and not authentication. OpenAPI describes Cognito bearer JWT; real JWT validation is not implemented.
- Pagination token is opaque but not cryptographically signed; tenant is embedded and checked, adequate only for local mock behavior.
- HTTP 401/403/429 and Retry-After behavior are not implemented because there is no real identity provider or throttling layer in this local server.
- `document` is metadata only. There is no authorized upload, malware scanning, object storage, or file-size validation against actual bytes.
- Processing is simulated with a background thread and an amount-based demo rule; it is not an actual claims decision engine, queue, or Step Functions workflow.
- Reviewed the current synthetic examples: the list example omits `nextToken`, which is valid for a final page.

## Contract reconciliation update

**Date:** 2026-10-12

- Expanded the documented `409` response to include both idempotency conflicts and duplicate client references.
- Clarified that the local mock's `413` response concerns its 16,384-byte JSON request-body limit. The declared document size is metadata only; no file upload is implemented.
- Made `updatedAt` required in the `Claim` schema and `statusUrl` required in `ClaimSubmissionAccepted`, matching the current local response shapes.
- Reviewed the synthetic examples. The list example may omit `nextToken` when there is no next page.
- These are contract-documentation changes only. Cognito/JWT verification, production throttling, real uploads, and full OpenAPI conformance remain unimplemented or unverified.

## Latest validation update

**Date:** 2026-10-12

- Added a string-type guard for `document.contentType` before checking the supported media types. List and object values now follow the normal `400 INVALID_DOCUMENT` validation path.
- Extended `test_document_metadata_validation` with regression subtests for list and object values.
- Validation run: `python -B -m unittest discover -s tests -v` from the local API directory.
- Observed result: **22 test methods passed; exit code 0.** The two malformed-content-type cases run as subtests within the existing test method.
- The source and test changes were compared with the pre-edit backup; the diff contained only the intended validation guard and regression test.
- This is a local mock validation improvement, not evidence of full OpenAPI conformance or production security.

## Latest local verification — 2026-10-16

- Runtime: Python 3.13.
- Command: `py -3.13 -m unittest discover -s tests -p "test_*.py" -v`, run from the canonical local API directory.
- Observed result: **22 tests passed; exit code 0.**
- This is evidence for the tested local mock behavior only. It does not establish full OpenAPI conformance, real authentication, production authorization, or production security.
- No AWS infrastructure operations were performed during this test run.

## Verification
Run `python -m unittest discover -s tests -v` from the local API directory. The test suite asserts the contract-relevant shapes and negative cases.
