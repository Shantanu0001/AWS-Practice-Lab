# Documentation Index

This index separates project requirements, historical evidence, implementation guidance, and current validation status. A document describing a design or requirement does not, by itself, prove implementation or acceptance.

## Project baseline and architecture

- [Project baseline](00-project-baseline.md) — current recovery status and project boundaries.
- [MedFlow architecture and requirements](MedFlow.md) — project architecture and requirements.
- [Windows workstation baseline](03-windows-workstation-baseline.md) — workstation setup notes.
- [AWS CLI authentication](02-aws-cli-authentication.md) — authentication procedures.
- [Stage 1 network design](04-network-design-stage1.md) — original network design.

## Delivery stages and validation

- [Stage 2 completion record](05-stage2-completion.md) — bounded learning slices and their recorded outcomes.
- [Stage 3 requirements traceability matrix](06-stage3-requirements-traceability-matrix.md) — requirements and acceptance status.
- [Stage 3 network egress decision](07-stage3-network-egress-decision.md) — proposed network-egress approach and outstanding validation.
- [Portal/API integration mapping](07-portal-api-integration-mapping.md) — proposed field mapping and integration boundaries.

## Implementation and contract references

- [Local API implementation and run instructions](../medflow-local-api/medflow-local-api/README.md) — runnable local API with in-memory state. The standalone portal prototype is separate and is not integrated with this API.
- [Proposed OpenAPI contract](../medflow-api-contract/medflow-api-contract/README.md) — contract draft, examples, and acceptance checklist.
- [Standalone portal prototype](../medflow-portal-prototype/medflow-portal-prototype/README.md) — browser-only prototype; not integrated with the local API.
- [API contract conformance review](../CONTRACT-CONFORMANCE-REVIEW.md) — local mock alignment, recorded test results, and remaining security and conformance gaps.

These artifacts remain separate. The browser prototype is not integrated with the local API, and the proposed OpenAPI contract has not been fully validated for conformance.

## Evidence and security

- [Evidence index](../evidence/README.md) — available project evidence.
- [Security policy](../SECURITY.md) — security and handling boundaries.

## Status interpretation

Distinguish among proposed design, local test results, AWS configuration checks, and observed end-to-end acceptance evidence. Stage 3 acceptance remains pending where required tests have not been run. The default cloud-spend budget is INR 0; this index does not authorize deployment or resource changes.
