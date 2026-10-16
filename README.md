# MedFlow Claims — AWS Architecture and Security Learning Project

MedFlow Claims is a staged, evidence-driven AWS learning project based on a fictional claims-processing platform. It documents architecture decisions, bounded AWS implementation exercises, security controls, testing, troubleshooting, and teardown under a zero-cloud-spend default.

This repository is a learning portfolio, not a deployed production application or a claim of regulatory certification.

## Project status

| Area | Status | Evidence boundary |
|---|---|---|
| Stage 1 — AWS foundation | Historical implementation documented | Review the dated evidence and lifecycle records; this is not a claim that the environment is still running. |
| Stage 2 — AWS learning slices | Eight bounded exercises recorded as complete | Completion applies to the documented exercises, not to one integrated production platform. |
| Stage 3 — S3-01 network egress | Template validation completed; temporary deployment torn down | Egress behavior and Availability Zone failure acceptance tests remain pending. |
| Local API | Runnable demonstration | Uses in-memory state and is not a production backend. |
| API contract | Proposed OpenAPI contract | A contract and examples do not establish implementation conformance. |
| Portal prototype | Separate browser-only prototype | Not integrated with the local API. |

The default personal AWS budget is INR 0. No new AWS deployment is required to review this repository or run its local tests.

## Start here

1. [Project baseline](docs/00-project-baseline.md)
2. [Architecture and requirements](docs/MedFlow.md)
3. [Stage 2 completion record](docs/05-stage2-completion.md)
4. [Stage 3 requirements traceability matrix](docs/06-stage3-requirements-traceability-matrix.md)
5. [Stage 3 network egress decision](docs/07-stage3-network-egress-decision.md)
6. [Portal/API integration mapping](docs/07-portal-api-integration-mapping.md)
7. [Documentation index](docs/README.md)
8. [Security policy](SECURITY.md)

## Code and implementation

- [Local API, tests, and run instructions](medflow-local-api/medflow-local-api/README.md) — local demonstration with in-memory state. State resets when the process restarts.
- [Proposed API contract](medflow-api-contract/medflow-api-contract/README.md) — OpenAPI definition, example payloads, and acceptance material.
- [Portal prototype](medflow-portal-prototype/medflow-portal-prototype/README.md) — standalone browser prototype using browser-side storage.
- [Stage 3 starter pack](medflow-stage3-starter-pack-v2/medflow_stage3_starter/README.md) — network design, template, runbook, validation scripts, and tests.

## Validation

Latest verified local test run — 16 October 2026, Python 3.13:

- Canonical local API: 22 tests passed; exit code 0.
- Stage 3 v2 offline tests: 7 tests passed; exit code 0.
- Total: 29 passing tests across these two suites.
- No AWS infrastructure operations were performed during these test runs.

These results describe the specific local run above, not a fresh execution on every checkout. Offline unit tests do not prove successful AWS egress, resilience during an Availability Zone failure, production security, or end-to-end application integration. CloudFormation template validation is also not proof of deployed behavior.

Use the individual project READMEs for prerequisites and commands. Review the Stage 3 traceability matrix for acceptance criteria and outstanding evidence.

## Security and design boundaries

- Use synthetic data only; do not place real medical or personal data in this learning project.
- Treat the local API tenant selector as a demonstration input, not authentication or authorization.
- Do not treat the proposed API contract as proof that its security requirements are implemented.
- Keep credentials, private backups, unredacted AWS transcripts, and recovery material out of the public repository.
- Review changes and inspect the exact Git diff before committing.

## What this project demonstrates

The portfolio focuses on AWS architecture, security-aware design, infrastructure-as-code validation, API testing, technical documentation, evidence handling, cost control, and honest reporting of implementation gaps.

The main engineering outcome is a traceable record of what was attempted, what was validated, what was torn down, and what remains unverified—not a claim that the complete MedFlow platform is production-ready.
