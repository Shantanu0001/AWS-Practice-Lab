# MedFlow local mock API + connected portal

This is the next executable slice after the static portal and API contract: the browser now calls a local HTTP API instead of using browser local storage.

## Run on Windows PowerShell

1. Extract the ZIP to a folder, for example `.\medflow-local-api`.
2. Confirm Python 3.10+ is available: `python --version`.
3. In PowerShell, run:

   ```powershell
   cd .\medflow-local-api
   .\run.ps1
   ```

   Or use `python .\server.py`.
4. Open **http://127.0.0.1:8000** in your browser. Do not open `index.html` directly; the page and API are served from the same local server.
5. Switch workspaces, search/filter claims, submit a synthetic claim, and observe it move from `Processing` to the selected outcome after about four seconds.
6. Stop the server with `Ctrl+C`. All mock records reset when the server restarts.

## API routes

- `GET /v1/health`
- `GET /v1/claims?limit=25` (optional `status`, `limit`, `nextToken`) (optional `status=PROCESSING|ACCEPTED|MANUAL_REVIEW|REJECTED`)
- `POST /v1/claims` with `Idempotency-Key` header and JSON body
- `GET /v1/claims/{claimId}`

Example request body (document metadata is optional; no file bytes are uploaded):

```json
{
  "clientReference": "DEMO-LOCAL-001",
  "serviceDate": "2026-10-11",
  "amount": 125.50,
  "document": {"fileName":"synthetic-example.pdf","contentType":"application/pdf","sizeBytes":1024}
}
```

The `document.fileName`, `document.contentType`, and `document.sizeBytes` fields are metadata only. No document bytes are uploaded. API responses include `Cache-Control: no-store`; error payloads use the flat contract shape `{ "code", "message", "requestId" }`. The mock implements tenant-scoped list/detail lookups, validation, duplicate client-reference rejection, idempotency replay, and conflict on the same idempotency key with a different payload.

Frontend distinction: the interface bundled with this folder is served by and calls this local mock API. The separate `medflow-portal-prototype/medflow-portal-prototype/` project is a browser-only localStorage prototype and is not integrated with this API.

## Run API tests

From this directory:

```powershell
python -m unittest discover -s tests -v
```

Tests use a separate ephemeral localhost port and synthetic records. They cover contract response schemas, tenant-scoped lists, cross-tenant detail denial, idempotency validation/replay/conflict, document metadata validation, pagination, amount/date/reference constraints, and error response shape.

## Security and correctness boundary — important

- **Local learning mock only. Not production-safe.** No AWS resources are created or modified.
- `X-Demo-Tenant` deliberately simulates a workspace switch so you can test request flows. It is a client-controlled header and **is not authentication or authorization**. A user can forge it. Replace it with verified identity (for example, validated Cognito JWT claims) and server-derived tenant context before any real deployment.
- State and idempotency records are in memory, not durable, and reset on restart. The lock makes local concurrent operations coherent but does not model distributed persistence or queue consumers.
- The asynchronous status update is a background thread, not Step Functions/SQS/Lambda.
- File input reads the filename only. It does not upload, scan, or store the selected file.
- Bind is fixed to `127.0.0.1`; do not expose this mock to a network.
- Synthetic data only; never enter real patient or billing information.

## Suggested next implementation slice

Add contract-driven request/response tests against `openapi/medflow-claims-v1.yaml`, then replace the mock identity header with a real auth boundary in a separate implementation slice. Do not deploy until explicit approval and a cost/rollback plan.
