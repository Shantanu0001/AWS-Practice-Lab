import json
import threading
import unittest
import urllib.request
import urllib.error
import time

import server
from server import ThreadingHTTPServer, Handler


class APITests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.port = cls.httpd.server_address[1]
        cls.thread = threading.Thread(
            target=cls.httpd.serve_forever, daemon=True
        )
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.port}"

    def setUp(self):
        # Isolate test data while preserving the seeded demo claims.
        seeded_ids = {
            "CLM-1042", "CLM-1041", "CLM-1040", "CLM-1039",
            "CLM-2042", "CLM-2041",
        }
        with server.LOCK:
            for claim_id in list(server.claims):
                if claim_id not in seeded_ids:
                    del server.claims[claim_id]
            server.idempotency.clear()
            # Do not reset server.next_number: background processing
            # threads from earlier tests may still be finishing.

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def request(
        self, path, method="GET", tenant="northstar",
        body=None, key=None
    ):
        headers = {}
        if tenant is not None:
            headers["X-Demo-Tenant"] = tenant

        data = None

        if body is not None:
            headers["Content-Type"] = "application/json"
            data = json.dumps(body).encode()

        if key is not None:
            headers["Idempotency-Key"] = key

        req = urllib.request.Request(
            self.base + path,
            data=data,
            headers=headers,
            method=method,
        )

        try:
            with urllib.request.urlopen(req) as r:
                return r.status, json.loads(r.read()), dict(r.headers)
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read()), dict(e.headers)

    def valid_body(self, suffix=None):
        return {
            "clientReference": "TEST-" + (suffix or str(time.time_ns())),
            "serviceDate": "2026-10-11",
            "amount": 22.50,
        }

    def assert_error_schema(self, payload):
        self.assertEqual(
            set(payload), {"code", "message", "requestId"}
        )
        self.assertTrue(payload["code"])
        self.assertTrue(payload["message"])
        self.assertTrue(payload["requestId"])
        self.assertLessEqual(len(payload["message"]), 300)

    def test_health_and_no_store(self):
        code, body, headers = self.request("/v1/health")
        self.assertEqual(code, 200)
        self.assertEqual(body["status"], "ok")
        self.assertEqual(headers.get("Cache-Control"), "no-store")

    # ADDED: Health must work without a demo tenant header.
    def test_health_does_not_require_demo_tenant(self):
        code, payload, _ = self.request(
            "/v1/health", tenant=None
        )
        self.assertEqual(code, 200, payload)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["mode"], "local-mock")
        self.assertIs(payload["syntheticDataOnly"], True)

    def test_list_response_schema_and_tenant_scope(self):
        _, a, _ = self.request("/v1/claims", tenant="northstar")
        _, b, _ = self.request("/v1/claims", tenant="cedar")

        self.assertTrue(a["items"])
        self.assertTrue(b["items"])
        self.assertNotIn("count", a)
        if len(a["items"]) < 25:
            self.assertNotIn("nextToken", a)

        self.assertIn(
            "CLM-1042", {x["claimId"] for x in a["items"]}
        )
        self.assertNotIn(
            "CLM-2042", {x["claimId"] for x in a["items"]}
        )

        for claim in a["items"]:
            self.assertTrue({
                "claimId", "clientReference", "serviceDate",
                "amount", "status", "submittedAt",
            }.issubset(claim))

    def test_pagination_and_tenant_bound_token(self):
        _, first, _ = self.request("/v1/claims?limit=2")
        self.assertEqual(len(first["items"]), 2)
        self.assertIn("nextToken", first)

        _, second, _ = self.request(
            "/v1/claims?limit=2&nextToken=" + first["nextToken"]
        )
        self.assertEqual(len(second["items"]), 2)

        code, err, _ = self.request(
            "/v1/claims?limit=2&nextToken=" + first["nextToken"],
            tenant="cedar",
        )
        self.assertEqual(code, 400)
        self.assert_error_schema(err)

    def test_cross_tenant_detail_is_hidden(self):
        code, body, headers = self.request(
            "/v1/claims/CLM-1042", tenant="cedar"
        )
        self.assertEqual(code, 404)
        self.assert_error_schema(body)
        self.assertEqual(headers.get("Cache-Control"), "no-store")

    def test_detail_is_direct_claim_schema(self):
        code, claim, _ = self.request("/v1/claims/CLM-1042")
        self.assertEqual(code, 200)
        self.assertIn("claimId", claim)
        self.assertNotIn("claim", claim)

    def test_missing_idempotency_key_rejected(self):
        code, payload, _ = self.request(
            "/v1/claims", "POST", body=self.valid_body()
        )
        self.assertEqual(code, 400)
        self.assert_error_schema(payload)

    def test_short_idempotency_key_rejected(self):
        code, payload, _ = self.request(
            "/v1/claims", "POST",
            body=self.valid_body(), key="short"
        )
        self.assertEqual(code, 400)
        self.assertEqual(payload["code"], "INVALID_IDEMPOTENCY_KEY")

    def test_idempotency_replays_contract_response(self):
        body = self.valid_body()
        key = "test-replay-" + str(time.time_ns())

        c1, one, _ = self.request(
            "/v1/claims", "POST", body=body, key=key
        )
        c2, two, _ = self.request(
            "/v1/claims", "POST", body=body, key=key
        )

        self.assertEqual((c1, c2), (202, 202))
        self.assertEqual(one["claimId"], two["claimId"])
        self.assertEqual(one["status"], "PROCESSING")
        self.assertTrue(one.get("acceptedAt"))
        self.assertTrue(one.get("statusUrl"))
        self.assertEqual(
            set(one), {"claimId", "status", "acceptedAt", "statusUrl"}
        )

    def test_idempotency_replays_equivalent_amount_formats(self):
        body = self.valid_body()
        key = "test-decimal-" + str(time.time_ns())

        first_code, first, _ = self.request(
            "/v1/claims", "POST",
            body={**body, "amount": 22},
            key=key,
        )

        second_code, second, _ = self.request(
            "/v1/claims", "POST",
            body={**body, "amount": 22.00},
            key=key,
        )

        self.assertEqual(first_code, 202, first)
        self.assertEqual(second_code, 202, second)
        self.assertEqual(first["claimId"], second["claimId"])
        self.assertEqual(first["acceptedAt"], second["acceptedAt"])

    def test_idempotency_conflict(self):
        key = "test-conflict-" + str(time.time_ns())
        body = self.valid_body()

        self.request("/v1/claims", "POST", body=body, key=key)
        changed = {**body, "amount": 24.5}

        code, payload, _ = self.request(
            "/v1/claims", "POST", body=changed, key=key
        )
        self.assertEqual(code, 409)
        self.assertEqual(payload["code"], "IDEMPOTENCY_CONFLICT")
        self.assert_error_schema(payload)

    def test_invalid_status_rejected(self):
        code, payload, headers = self.request(
            "/v1/claims?status=BOGUS"
        )
        self.assertEqual(code, 400)
        self.assertEqual(payload["code"], "INVALID_STATUS")
        self.assertEqual(headers.get("Cache-Control"), "no-store")
        self.assert_error_schema(payload)

    def test_duplicate_client_reference_rejected_case_insensitively(self):
        body = {
            "clientReference": "demo-ref-218",
            "serviceDate": "2026-10-11",
            "amount": 22.50,
        }

        code, payload, _ = self.request(
            "/v1/claims", "POST",
            body=body,
            key="duplicate-ref-" + str(time.time_ns()),
        )
        self.assertEqual(code, 409)
        self.assertEqual(
            payload["code"], "DUPLICATE_CLIENT_REFERENCE"
        )

    def test_invalid_service_date_rejected(self):
        body = self.valid_body()
        body["serviceDate"] = "not-a-date"

        code, payload, _ = self.request(
            "/v1/claims", "POST",
            body=body,
            key="bad-date-" + str(time.time_ns()),
        )
        self.assertEqual(code, 400)
        self.assertEqual(payload["code"], "INVALID_SERVICE_DATE")

    def test_invalid_amount_values_rejected(self):
        for amount in [0, -1, 100000000, True, "22.50", 1.234]:
            with self.subTest(amount=amount):
                body = self.valid_body()
                body["amount"] = amount

                code, payload, _ = self.request(
                    "/v1/claims", "POST",
                    body=body,
                    key="bad-amount-" + str(time.time_ns()),
                )
                self.assertEqual(code, 400)
                self.assertEqual(payload["code"], "INVALID_AMOUNT")

    def test_reference_pattern_and_length(self):
        for ref in ["contains space", "bad/ref", "x" * 65]:
            body = self.valid_body()
            body["clientReference"] = ref

            code, payload, _ = self.request(
                "/v1/claims", "POST",
                body=body,
                key="bad-ref-" + str(time.time_ns()),
            )
            self.assertEqual(code, 400)
            self.assertEqual(
                payload["code"], "INVALID_CLIENT_REFERENCE"
            )

    # Tenant validation tests

    def test_missing_tenant_header_rejected(self):
        code, payload, _ = self.request(
            "/v1/claims", "GET", tenant=None
        )
        self.assertEqual(code, 400)
        self.assertEqual(payload["code"], "INVALID_DEMO_TENANT")

    def test_empty_tenant_header_rejected(self):
        code, payload, _ = self.request(
            "/v1/claims", "GET", tenant=""
        )
        self.assertEqual(code, 400)
        self.assertEqual(payload["code"], "INVALID_DEMO_TENANT")

    def test_unknown_tenant_header_rejected(self):
        code, payload, _ = self.request(
            "/v1/claims", "GET", tenant="unknown-tenant"
        )
        self.assertEqual(code, 400)
        self.assertEqual(payload["code"], "INVALID_DEMO_TENANT")

    def test_unknown_submission_field_rejected(self):
        body = self.valid_body()
        body["tenantId"] = "cedar"

        code, payload, _ = self.request(
            "/v1/claims", "POST",
            body=body,
            key="unknown-field-" + str(time.time_ns()),
        )
        self.assertEqual(code, 400)
        self.assertEqual(payload["code"], "UNKNOWN_FIELDS")

    def test_document_metadata_validation(self):
        body = self.valid_body()
        body["document"] = {
            "fileName": "demo.pdf",
            "contentType": "application/pdf",
            "sizeBytes": 1024,
        }

        code, payload, _ = self.request(
            "/v1/claims", "POST",
            body=body,
            key="valid-doc-" + str(time.time_ns()),
        )
        self.assertEqual(code, 202)
        self.assertIn("acceptedAt", payload)

        bad = self.valid_body()
        bad["document"] = {
            "fileName": "demo.exe",
            "contentType": "application/x-msdownload",
            "sizeBytes": 1024,
        }

        code, payload, _ = self.request(
            "/v1/claims", "POST",
            body=bad,
            key="bad-doc-" + str(time.time_ns()),
        )
        self.assertEqual(code, 400)
        self.assertEqual(payload["code"], "INVALID_DOCUMENT")

        # Malformed contentType values must return a validation error.
        for invalid_content_type in (
            ["application/pdf"],
            {"type": "application/pdf"},
        ):
            with self.subTest(contentType=invalid_content_type):
                malformed = self.valid_body()
                malformed["document"] = {
                    "fileName": "demo.pdf",
                    "contentType": invalid_content_type,
                    "sizeBytes": 1024,
                }

                code, payload, headers = self.request(
                    "/v1/claims", "POST",
                    body=malformed,
                    key="bad-type-" + str(time.time_ns()),
                )

                self.assertEqual(code, 400, payload)
                self.assertEqual(payload["code"], "INVALID_DOCUMENT")
                self.assert_error_schema(payload)
                self.assertEqual(headers.get("Cache-Control"), "no-store")

    def test_error_response_has_flat_contract_shape(self):
        code, payload, headers = self.request(
            "/v1/claims?status=BOGUS"
        )
        self.assertEqual(code, 400)
        self.assert_error_schema(payload)
        self.assertTrue(payload["requestId"])
        self.assertEqual(headers.get("Cache-Control"), "no-store")


if __name__ == "__main__":
    unittest.main(verbosity=2)