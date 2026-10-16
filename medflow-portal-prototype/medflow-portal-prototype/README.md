# MedFlow Claims Portal — local frontend prototype

A dependency-free, browser-only UI prototype for the MedFlow Claims Learning Lab. It is intended to make the portal workflow concrete before connecting it to AWS.

## Run it

1. Extract this folder.
2. Open `index.html` in a current browser.
3. Switch between the two demo workspaces, search/filter claims, and submit a synthetic claim.
4. Choose a simulated outcome. The claim first appears as **Processing**, then changes to the selected outcome after about 4.5 seconds.

No build step, package manager, cloud account, or AWS resources are required.

## Included

- Overview cards and recent claims table
- Demo workspace switcher with per-workspace claim lists
- Search and status filtering
- Claim submission form with client reference, service date, amount, optional local filename, and simulated outcome
- Processing → final-outcome UI simulation
- Browser local storage for demo records
- Duplicate client-reference check within the current workspace
- An idempotency-key-shaped demo value shown in the record detail dialog

## Important boundaries

This is **not a production application** and does not implement authentication, authorization, tenant isolation, a backend API, durable idempotency, real document upload, or real claim processing.

- Workspace switching is a UI demonstration, not a security boundary.
- File selection only reads the filename. The file is not uploaded or stored.
- Claims are synthetic. Never enter real patient, medical, or billing information.
- Browser local storage is not a secure database.
- The generated key is only a frontend demo value. The backend must enforce idempotency on the server.
- No AWS resources were created or modified.

## Next integration steps

1. Agree and document API request/response contracts.
2. Add the real identity flow (Cognito or the identity approach recorded in the project source) and derive tenant identity from verified claims on the server. Do not trust a tenant ID supplied by the browser.
3. Connect claim submission to a backend endpoint and return an accepted claim ID quickly; processing should remain asynchronous.
4. Upload documents through a backend-authorized flow (for example, short-lived presigned upload authorization) and enforce server-side size/type/content checks.
5. Fetch claim lists/details using server-side tenant scoping. Responses containing tenant-specific claim data must use `Cache-Control: no-store` and must not be cached by CloudFront.
6. Host the compiled/static frontend in a private S3 bucket served by CloudFront Origin Access Control. Keep S3 direct public access blocked.
7. Add tests for cross-tenant access denial, duplicate submissions, API errors, and eventual status updates.

## File layout

- `index.html` — semantic page structure and claim form
- `styles.css` — responsive styling
- `app.js` — synthetic demo data and local UI interactions
