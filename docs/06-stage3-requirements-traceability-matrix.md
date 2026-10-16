# Stage 3 — Requirements Traceability Matrix

**Project:** MedFlow Claims
**Source of truth:** `docs/MedFlow.md`, §8.3 and related requirements
**Stage:** 3 — Production Architecture
**Status:** Planning only; no Stage 3 resources authorized by this document.

## Evidence rules

- **Implemented:** supported by observed implementation evidence.
- **Partial:** only a bounded part of the requirement was demonstrated.
- **Not implemented:** no implementation evidence is established.
- **Pending validation:** configuration or deployment alone is insufficient to prove the requirement.
- Stage 1/2 completion does not imply Stage 3 completion.
- Use synthetic data only. Preserve cost guardrails and teardown evidence.

## Requirements

| ID | Original requirement | Source | Existing evidence / dependency | Required validation | Cost and security considerations | Proposed slice | Status |
|---|---|---|---|---|---|---|---|
| S3-01 | Deploy one NAT Gateway per AZ so loss of one AZ does not remove egress for surviving workloads. | §8.3 | Stack `medflow-stage3-s3-01-network-egress` was deployed and then deleted. Both NAT Gateways reported `deleted`; the lookup for both original Elastic IP allocations returned no matching allocations. App subnets were restored to the original shared application route table. Evidence: sanitized public summary `evidence/stage3-s3-01-teardown-summary.md`; detailed source evidence is retained locally and is not included in the public summary. | Verify subnet routes and egress independently in both AZs; test the planned failure scenario. | NAT hourly and data-processing charges; avoid cross-AZ routing where possible. | Network foundation | Pending validation |
| S3-02 | Make app, cache, and database fault domains tolerate loss of one AZ without operator intervention. | §8.3; Failure Lab #2 | Stage 2 Slice A and B were bounded tests, not proof of full app/cache/database AZ resilience. Redis was not deployed. | Conduct a controlled AZ/fault-domain test and record recovery behavior and measured impact. | Multi-AZ capacity and data transfer add cost. | Resilience foundation | Not implemented |
| S3-03 | Make Step Functions states and SQS consumers safely re-runnable; upsert claim records using a client-supplied idempotency key. | §8.3 | Stage 2 tested a bounded SQS/DLQ/Step Functions workflow; production-style claim persistence and idempotency were not demonstrated. | Replay duplicate messages and workflow steps; prove one logical claim result and safe recovery. | Duplicate processing can cause data corruption or repeated side effects. | Processing reliability | Not implemented |
| S3-04 | Apply exponential backoff with jitter to Lambda external-API calls and Step Functions retries. | §8.3 | Stage 2 workflow was a bounded learning exercise; no evidence establishes this retry policy across the target workflow. | Inspect retry policies and test transient failures, retry limits, and terminal failure handling. | Prevent retry storms, excess invocations, and downstream overload. | Processing reliability | Not implemented |
| S3-05 | If ElastiCache is unavailable, fall back to RDS with a shorter cache-miss timeout. | §8.3; Failure Lab #6 | ElastiCache was not deployed in the bounded Stage 2 work. | Simulate cache failure and verify the request path falls back safely without unacceptable latency or database overload. | Database connection capacity and fallback load need guardrails. | Data resilience | Not implemented |
| S3-06 | Configure health checks at ALB, Route 53 where applicable, and ECS task level, with task health linked to ALB deregistration. | §8.3 | Stage 2 Slice A used an ALB/ASG test, but Route 53 and ECS task-health integration were not established. | Test unhealthy targets, task replacement, deregistration, and DNS failover behavior where configured. | Route 53 requires domain/DNS decisions; health checks must detect meaningful failures. | Health and recovery | Partial |
| S3-07 | Stop tenant-webhook delivery after N consecutive failures and raise a CloudWatch alarm. | §8.3 | No implemented notifier circuit breaker is established by current evidence. | Cause repeated endpoint failures; verify breaker behavior, alarm, and controlled recovery. | Avoid infinite retries and unnecessary Lambda charges; isolate failures per tenant. | Event-delivery resilience | Not implemented |
| S3-08 | Transition processed documents to S3 Standard-IA after 30 days and Glacier Deep Archive after one year, subject to the retention requirements. | §8.3; §5.5 | Stage 2 validated a temporary SSE-KMS S3 bucket, which was removed. No current bucket was returned by the inventory. | Validate lifecycle rules on synthetic objects and confirm expected transitions and retention behavior. | Retrieval/transition charges; ensure lifecycle does not violate the seven-year retention floor. | Storage lifecycle | Not implemented |
| S3-09 | Put CloudFront in front of the static portal SPA and appropriate read-heavy public API responses; restrict the S3 origin using Origin Access Control. | §8.3 | No CloudFront deployment is established by Stage 2 evidence. | Verify distribution behavior, cache policy, origin access restrictions, and direct-origin denial. Keep dynamic claim responses uncached unless explicitly safe. | Distribution/request/data-transfer charges; avoid caching tenant-sensitive responses. | Edge delivery | Not implemented |
| S3-10 | Centralize CloudTrail, VPC Flow Logs, ALB access logs, S3 access logs, and application logs in a dedicated archive bucket with Object Lock governance mode. | §8.3; §10.4 | Stage 1 validated a temporary management-event trail; Stage 2 created two test log groups. No current S3 bucket or CloudTrail trail was returned by the inventory. Organization trail is Production-Style only. | Verify each source is delivered, access is restricted, retention is configured, and Object Lock behavior is tested. | Log ingestion/storage and data-event costs; protect evidence from accidental deletion. | Observability and audit | Partial |
| S3-11 | Create an AWS Backup plan for applicable RDS, DynamoDB, and EFS/EBS resources; schedule quarterly restore-to-scratch tests. | §8.3; Failure Lab #11 | No backup-plan implementation or restore drill is established by current evidence. | Restore into an isolated scratch environment and record actual recovery time and data recovery point. | Backup storage and retention costs; backup existence alone does not prove recoverability. | Backup and recovery | Not implemented |
| S3-12 | Use ECS rolling/blue-green deployments through CodeDeploy with automatic rollback; use versioned Lambda aliases and weighted traffic shifting. | §8.3 | Stage 2 tested an ASG/ALB CloudFormation slice and a Lambda authorizer; no ECS CodeDeploy deployment or weighted Lambda rollout is established. | Deploy a controlled bad version; verify health-based rollback and alias traffic behavior. | Temporary duplicate capacity and deployment complexity; preserve a known-good revision. | Release engineering | Not implemented |
| S3-13 | Manage 100% of Stage 3 infrastructure with CloudFormation, separated into network, data, compute, and security stacks. | §8.3 | Stage 2 Slice H validated a bounded CloudFormation template; full Stage 3 infrastructure-as-code coverage is not established. | Validate templates, review change sets, deploy from code, and verify teardown/rebuild reproducibility. | Avoid unmanaged resources and unexpected replacement; use least-privilege deployment permissions. | IaC foundation | Partial |

## Readiness gates before implementation

1. Confirm the active AWS profile, region, and account.
2. Review budget alerts and the expected cost of the chosen slice.
3. Inspect existing resources and dependencies before deployment.
4. Define the exact success criteria, failure test, evidence to retain, and teardown procedure.
5. Use CloudFormation where practical and inspect the change set before applying it.
6. Do not claim a requirement is complete until its validation evidence exists.
7. Reconcile actual implementation and resource state after teardown.

## Recommended planning order

1. IaC and network design review.
2. Costed network/resilience prototype.
3. Health checks and fault-domain validation.
4. Idempotency and retry behavior.
5. Cache degradation and webhook circuit breaker.
6. Logging, backup/restore, and deployment rollback.
7. S3 lifecycle and CloudFront after data-access and caching requirements are validated.

This order is a proposed implementation sequence, not a change to the original Stage 3 requirements.
