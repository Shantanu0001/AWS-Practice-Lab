# MedFlow local mock API + connected portal

This is the next executable slice after the static portal and API contract: the browser now calls a local HTTP API instead of using browser local storage.

## Run on Windows PowerShell

### Option 1: Run from the cloned repository

From the repository root (`D:\AWS-Practice-Lab`), run:

```powershell
Set-Location "D:\AWS-Practice-Lab\medflow-local-api\medflow-local-api"
.\run.ps1
```

Alternatively, start the server directly with:

```powershell
python .\server.py
```

### Option 2: Run from an extracted ZIP

1. Extract the project ZIP.
2. Open PowerShell in the extracted project directory containing `run.ps1` and `server.py`.
3. Confirm Python 3.10+ is available:

   ```powershell
   python --version
   ```

4. Start the server:

   ```powershell
   .\run.ps1
   ```

   Alternatively:

   ```powershell
   python .\server.py
   ```

5. Open **http://127.0.0.1:8000** in your browser. Do not open `index.html` directly; the page and API are served by the same local server.
6. Switch workspaces, search and filter claims, submit a synthetic claim, and observe it move from `Processing` to the selected outcome after about four seconds.
7. Stop the server with `Ctrl+C`. All mock records reset when the server restarts.

## API routes

- `GET /v1/health`
- `GET /v1/claims?limit=25` — supports optional `status`, `limit`, and `nextToken` query parameters. Supported statuses are `PROCESSING`, `ACCEPTED`, `MANUAL_REVIEW`, and `REJECTED`.
- `POST /v1/claims` — accepts a JSON body and an `Idempotency-Key` header.
- `GET /v1/claims/{claimId}`

### Example request body

Document metadata is optional. This example does not upload document bytes.

```json
{
  "clientReference": "DEMO-LOCAL-001",
  "serviceDate": "2026-10-11",
  "amount": 125.50,
  "document": {
    "fileName": "synthetic-example.pdf",
    "contentType": "application/pdf",
    "sizeBytes": 1024
  }
}
```

The `document.fileName`, `document.contentType`, and `document.sizeBytes` fields are metadata only. No document bytes are uploaded.

API responses include `Cache-Control: no-store`. Error payloads use the flat contract shape:

```json
{
  "code": "ERROR_CODE",
  "message": "Human-readable error message",
  "requestId": "request-id"
}
```

The mock implements tenant-scoped list and detail lookups, validation, duplicate client-reference rejection, idempotency replay, and conflict handling when the same idempotency key is reused with a different payload.

### Frontend distinction

The interface bundled with this folder is served by and calls this local mock API. The separate `medflow-portal-prototype/medflow-portal-prototype/` project is a browser-only `localStorage` prototype and is **not integrated** with this API.

## Run API tests

From the API project directory:

```powershell
python -m unittest discover -s tests -v
```

Tests use a separate ephemeral localhost port and synthetic records. They cover contract response schemas, tenant-scoped lists, cross-tenant detail denial, idempotency validation/replay/conflict, document metadata validation, pagination, amount/date/reference constraints, and error response shape.

## Security and correctness boundary — important

- **Local learning mock only. Not production-safe.** Running this project does not create or modify AWS resources.
- `X-Demo-Tenant` deliberately simulates a workspace switch so you can test request flows. It is a client-controlled header and **is not authentication or authorization**; a user can forge it. Before any real deployment, replace it with verified identity (for example, validated Cognito JWT claims) and server-derived tenant context.
- State and idempotency records are in memory, not durable, and reset on restart. The lock makes local concurrent operations coherent but does not model distributed persistence or queue consumers.
- The asynchronous status update is implemented with a background thread, not Step Functions, SQS, or Lambda.
- File input reads the filename only. It does not upload, scan, or store the selected file.
- The server binds to `127.0.0.1`; do not expose this mock to a network.
- Use synthetic data only. Never enter real patient or billing information.

## Suggested next implementation slice

Add contract-driven request/response tests against `openapi/medflow-claims-v1.yaml`, then replace the mock identity header with a real authentication boundary in a separate implementation slice.

Do not deploy until there is explicit approval and a documented cost and rollback plan.
