#!/usr/bin/env python3
"""Local-only MedFlow API mock aligned to the proposed OpenAPI contract."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timezone, date
from decimal import Decimal, InvalidOperation
import base64, json, threading, time, uuid, re

ROOT = Path(__file__).resolve().parent
HOST, PORT = "127.0.0.1", 8000
LOCK = threading.RLock()
TENANTS = {"northstar": "Northstar Billing", "cedar": "Cedar Health Admin"}
VALID_STATUSES = {"PROCESSING", "ACCEPTED", "MANUAL_REVIEW", "REJECTED"}
claims, idempotency = {}, {}
next_number = 3000


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def to_api(record):
    result = {
        "claimId": record["claimId"],
        "clientReference": record["clientReference"],
        "serviceDate": record["serviceDate"],
        "amount": float(record["amount"]),
        "status": record["status"],
        "submittedAt": record["submittedAt"],
        "updatedAt": record["updatedAt"],
    }
    if record.get("statusReason"):
        result["statusReason"] = record["statusReason"]
    return result


def seed(tenant, claim_id, ref, amount, status, filename=None, content_type=None):
    timestamp = now()
    claims[claim_id] = {
        "claimId": claim_id,
        "tenant": tenant,
        "clientReference": ref,
        "serviceDate": date.today().isoformat(),
        "amount": Decimal(str(amount)),
        "status": status,
        "submittedAt": timestamp,
        "updatedAt": timestamp,
        "createdEpoch": time.time(),
        "outcome": status,
        "statusReason": None,
        "document": (
            {
                "fileName": filename,
                "contentType": content_type,
                "sizeBytes": 1,
            }
            if filename else None
        ),
    }


seed("northstar", "CLM-1042", "DEMO-REF-218", 425.00, "PROCESSING",
     "example-claim.pdf", "application/pdf")
seed("northstar", "CLM-1041", "DEMO-REF-217", 189.50, "ACCEPTED",
     "synthetic-document.tif", "image/tiff")
seed("northstar", "CLM-1040", "DEMO-REF-216", 760.25, "MANUAL_REVIEW",
     "sample-claim.pdf", "application/pdf")
seed("northstar", "CLM-1039", "DEMO-REF-215", 92.00, "REJECTED",
     "demo-file.pdf", "application/pdf")
seed("cedar", "CLM-2042", "CEDAR-DEMO-09", 312.75, "ACCEPTED",
     "cedar-example.pdf", "application/pdf")
seed("cedar", "CLM-2041", "CEDAR-DEMO-08", 540.00, "PROCESSING",
     "cedar-sample.tif", "image/tiff")


def encode_token(tenant, offset):
    raw = f"{tenant}:{offset}".encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def decode_token(token, tenant):
    try:
        raw = base64.urlsafe_b64decode(
            token + "=" * (-len(token) % 4)
        ).decode()
        token_tenant, raw_offset = raw.split(":", 1)
        offset = int(raw_offset)
        if token_tenant != tenant or offset < 0:
            return None
        return offset
    except (ValueError, UnicodeDecodeError):
        return None


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    server_version = "MedFlowLocalMock/1.1"

    def log_message(self, fmt, *args):
        print("[http] " + (fmt % args))

    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        if self.path.startswith("/v1/"):
            self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header(
            "Access-Control-Allow-Origin",
            "http://127.0.0.1:8000",
        )
        self.send_header(
            "Access-Control-Allow-Methods",
            "GET, POST, OPTIONS",
        )
        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type, Idempotency-Key, X-Demo-Tenant",
        )
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

    def send_json(self, status, payload):
        raw = json.dumps(payload, separators=(",", ":")).encode()
        self.send_response(status)
        self.send_header(
            "Content-Type", "application/json; charset=utf-8"
        )
        self.send_header("Content-Length", str(len(raw)))
        self.send_header(
            "Access-Control-Allow-Origin",
            "http://127.0.0.1:8000",
        )
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def error(self, status, code, message):
        self.send_json(
            status,
            {
                "code": code,
                "message": message[:300],
                "requestId": str(uuid.uuid4()),
            },
        )

    def tenant(self):
        # Local demo tenant selector only; this is not authentication.
        raw_value = self.headers.get("X-Demo-Tenant")
        if raw_value is None or not raw_value.strip():
            return None
        value = raw_value.strip().lower()
        return value if value in TENANTS else None

    def read_body(self):
        try:
            length_text = self.headers.get("Content-Length", "0")
            length = int(length_text)
            if length < 0:
                return None, "invalid_json"
            if length > 16_384:
                return None, "too_large"
            raw = self.rfile.read(length)
            obj = json.loads(raw or b"{}")
            if not isinstance(obj, dict):
                return None, "invalid_json"
            return obj, None
        except (ValueError, json.JSONDecodeError):
            return None, "invalid_json"

    def do_GET(self):
        parsed = urlparse(self.path)
        if not parsed.path.startswith("/v1/"):
            return super().do_GET()

        # Health check runs before tenant validation.
        if parsed.path == "/v1/health":
            return self.send_json(
                200,
                {
                    "status": "ok",
                    "mode": "local-mock",
                    "syntheticDataOnly": True,
                },
            )

        tenant = self.tenant()
        if not tenant:
            return self.error(
                400,
                "INVALID_DEMO_TENANT",
                "Choose a supported local demo workspace.",
            )

        if parsed.path == "/v1/claims":
            query = parse_qs(parsed.query)
            status = query.get("status", [""])[0].upper()

            if status and status not in VALID_STATUSES:
                return self.error(
                    400, "INVALID_STATUS",
                    "Status filter is not supported.",
                )

            try:
                limit = int(query.get("limit", ["25"])[0])
            except ValueError:
                return self.error(
                    400, "INVALID_LIMIT",
                    "Limit must be an integer from 1 to 100.",
                )

            if not 1 <= limit <= 100:
                return self.error(
                    400, "INVALID_LIMIT",
                    "Limit must be an integer from 1 to 100.",
                )

            token_values = query.get("nextToken", [])
            offset = 0

            if token_values:
                offset = decode_token(token_values[0], tenant)
                if offset is None:
                    return self.error(
                        400,
                        "INVALID_NEXT_TOKEN",
                        "nextToken is invalid for this workspace.",
                    )

            with LOCK:
                records = [
                    c for c in claims.values()
                    if c["tenant"] == tenant
                    and (not status or c["status"] == status)
                ]
                records.sort(
                    key=lambda c: c["submittedAt"],
                    reverse=True,
                )
                total = len(records)
                page = records[offset:offset + limit]

            payload = {"items": [to_api(c) for c in page]}

            if offset + limit < total:
                payload["nextToken"] = encode_token(
                    tenant, offset + limit
                )

            return self.send_json(200, payload)

        match = re.fullmatch(
            r"/v1/claims/(CLM-[A-Z0-9-]{3,40})",
            parsed.path,
        )

        if match:
            with LOCK:
                record = claims.get(match.group(1))

            if not record or record["tenant"] != tenant:
                return self.error(
                    404,
                    "CLAIM_NOT_FOUND",
                    "The requested claim was not found.",
                )

            return self.send_json(200, to_api(record))

        return self.error(
            404, "NOT_FOUND",
            "The requested endpoint was not found.",
        )

    def do_POST(self):
        parsed = urlparse(self.path)

        if parsed.path != "/v1/claims":
            return self.error(
                404, "NOT_FOUND",
                "The requested endpoint was not found.",
            )

        tenant = self.tenant()
        if not tenant:
            return self.error(
                400,
                "INVALID_DEMO_TENANT",
                "Choose a supported local demo workspace.",
            )

        body, err = self.read_body()

        if err == "too_large":
            return self.error(
                413,
                "REQUEST_TOO_LARGE",
                "Request body exceeds the local demo limit.",
            )

        if err:
            return self.error(
                400, "INVALID_JSON",
                "Request body must be a JSON object.",
            )

        allowed = {
            "clientReference", "serviceDate", "amount", "document"
        }

        if set(body) - allowed:
            return self.error(
                400, "UNKNOWN_FIELDS",
                "Request contains unsupported fields.",
            )

        ref = body.get("clientReference")
        svc = body.get("serviceDate")
        amount = body.get("amount")

        if (
            not isinstance(ref, str)
            or not (1 <= len(ref) <= 64)
            or not re.fullmatch(r"[A-Za-z0-9._-]+", ref)
        ):
            return self.error(
                400,
                "INVALID_CLIENT_REFERENCE",
                "clientReference must be 1-64 letters, digits, dots, "
                "underscores, or hyphens.",
            )

        if not isinstance(svc, str):
            return self.error(
                400,
                "INVALID_SERVICE_DATE",
                "serviceDate must use YYYY-MM-DD format.",
            )

        try:
            parsed_date = date.fromisoformat(svc)
            if parsed_date.isoformat() != svc:
                raise ValueError()
        except ValueError:
            return self.error(
                400,
                "INVALID_SERVICE_DATE",
                "serviceDate must use YYYY-MM-DD format.",
            )

        if isinstance(amount, bool) or not isinstance(
            amount, (int, float)
        ):
            return self.error(
                400,
                "INVALID_AMOUNT",
                "amount must be a number from 0.01 to 99999999.99 "
                "with at most two decimals.",
            )

        try:
            decimal_amount = Decimal(str(amount))
        except InvalidOperation:
            return self.error(
                400,
                "INVALID_AMOUNT",
                "amount must be a valid decimal number.",
            )

        if (
            not decimal_amount.is_finite()
            or decimal_amount < Decimal("0.01")
            or decimal_amount > Decimal("99999999.99")
            or decimal_amount != decimal_amount.quantize(
                Decimal("0.01")
            )
        ):
            return self.error(
                400,
                "INVALID_AMOUNT",
                "amount must be a number from 0.01 to 99999999.99 "
                "with at most two decimals.",
            )

        document = body.get("document")

        if document is not None:
            if (
                not isinstance(document, dict)
                or set(document) - {
                    "fileName", "contentType", "sizeBytes"
                }
                or not {
                    "fileName", "contentType", "sizeBytes"
                }.issubset(document)
            ):
                return self.error(
                    400,
                    "INVALID_DOCUMENT",
                    "document must include fileName, contentType, "
                    "and sizeBytes only.",
                )

            name = document.get("fileName")
            content_type = document.get("contentType")
            size = document.get("sizeBytes")

            if not isinstance(name, str) or not 1 <= len(name) <= 255:
                return self.error(
                    400,
                    "INVALID_DOCUMENT",
                    "document.fileName must be 1-255 characters.",
                )

            if (
                not isinstance(content_type, str)
                or content_type not in {
                    "application/pdf", "image/tiff"
                }
            ):
                return self.error(
                    400,
                    "INVALID_DOCUMENT",
                    "document.contentType must be application/pdf "
                    "or image/tiff.",
                )

            if (
                isinstance(size, bool)
                or not isinstance(size, int)
                or not 1 <= size <= 26214400
            ):
                return self.error(
                    400,
                    "INVALID_DOCUMENT",
                    "document.sizeBytes must be an integer from "
                    "1 to 26214400.",
                )

        key = self.headers.get("Idempotency-Key", "")

        if not 8 <= len(key) <= 128:
            return self.error(
                400,
                "INVALID_IDEMPOTENCY_KEY",
                "Idempotency-Key must be 8-128 characters.",
            )

        # UPDATED: Normalize the amount to exactly two decimal places.
        normalized = json.dumps(
            {
                "clientReference": ref,
                "serviceDate": svc,
                "amount": format(
                    decimal_amount.quantize(Decimal("0.01")),
                    ".2f",
                ),
                "document": document,
            },
            sort_keys=True,
            separators=(",", ":"),
        )

        ikey = (tenant, key)
        global next_number

        with LOCK:
            if ikey in idempotency:
                prior_payload, prior_id, accepted_at = idempotency[ikey]

                if prior_payload != normalized:
                    return self.error(
                        409,
                        "IDEMPOTENCY_CONFLICT",
                        "This Idempotency-Key was already used "
                        "with a different request.",
                    )

                return self.send_json(
                    202,
                    {
                        "claimId": prior_id,
                        "status": "PROCESSING",
                        "acceptedAt": accepted_at,
                        "statusUrl": f"/v1/claims/{prior_id}",
                    },
                )

            if any(
                c["tenant"] == tenant
                and c["clientReference"].lower() == ref.lower()
                for c in claims.values()
            ):
                return self.error(
                    409,
                    "DUPLICATE_CLIENT_REFERENCE",
                    "A claim with this client reference already "
                    "exists in this workspace.",
                )

            next_number += 1
            cid = f"CLM-{next_number}"
            accepted_at = now()

            record = {
                "claimId": cid,
                "tenant": tenant,
                "clientReference": ref,
                "serviceDate": svc,
                "amount": decimal_amount,
                "status": "PROCESSING",
                "submittedAt": accepted_at,
                "updatedAt": accepted_at,
                "statusReason": None,
                "document": document,
                "outcome": (
                    "MANUAL_REVIEW"
                    if decimal_amount >= Decimal("10000")
                    else "ACCEPTED"
                ),
                "createdEpoch": time.time(),
            }

            claims[cid] = record
            idempotency[ikey] = (normalized, cid, accepted_at)

        threading.Thread(
            target=self.finish_processing,
            args=(cid,),
            daemon=True,
        ).start()

        self.send_json(
            202,
            {
                "claimId": cid,
                "status": "PROCESSING",
                "acceptedAt": accepted_at,
                "statusUrl": f"/v1/claims/{cid}",
            },
        )

    @staticmethod
    def finish_processing(cid):
        time.sleep(4)

        with LOCK:
            record = claims.get(cid)

            if record and record["status"] == "PROCESSING":
                record["status"] = record["outcome"]
                record["updatedAt"] = now()

                if record["status"] == "MANUAL_REVIEW":
                    record["statusReason"] = (
                        "Amount flagged for manual review in the local demo."
                    )


if __name__ == "__main__":
    print("MedFlow local mock API starting at http://127.0.0.1:8000")
    print("Local-only synthetic data. Demo tenant header is NOT authentication.")
    print("Press Ctrl+C to stop. In-memory records reset when server restarts.")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()