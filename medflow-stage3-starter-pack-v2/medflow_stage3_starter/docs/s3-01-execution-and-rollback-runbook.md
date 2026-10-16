# S3-01 Execution and Rollback Runbook

**Project:** AWS-Project-MedFlow
**Requirement:** S3-01 — Multi-AZ network-egress resilience
**Prepared:** 2026-10-12
**Status:** Draft — deployment not authorized

## 1. Objective

Implement and validate one NAT Gateway per Availability Zone, with a dedicated
application route table for each AZ. Demonstrate independent egress and assess
the planned AZ/NAT failure scenario.

## 2. Current baseline

- Region: us-east-1
- VPC: [VPC_ID]
- App-A subnet: [APP_A_SUBNET_ID]
- App-B subnet: [APP_B_SUBNET_ID]
- Public-A subnet: [PUBLIC_A_SUBNET_ID]
- Public-B subnet: [PUBLIC_B_SUBNET_ID]
- Original shared application route table: [APP_ROUTE_TABLE_ID]
- Public route table: [PUBLIC_ROUTE_TABLE_ID]
- Data route table: [DATA_ROUTE_TABLE_ID]
- Main route table: [MAIN_ROUTE_TABLE_ID]

The baseline review recorded both app subnets associated with the shared
application route table. The public route table has an active default route
to the Internet Gateway. The data and main route tables have only the VPC
local route in the inspected baseline.

## 3. Proposed change set

- Stack: medflow-stage3-s3-01-network-egress
- Change set: s3-01-review-20261011
- Recorded status: CREATE_COMPLETE
- Recorded execution status: AVAILABLE
- Description explicitly says review only; not approved for execution.
- Reviewed plan: 10 additions, no deletions or replacements reported.
- Missing ChangeSetType in DescribeChangeSet is not a deployment blocker by
  itself; it is not a documented response field.

## 4. Preconditions — all required before execution

- Obtain explicit deployment approval.
- Re-read the change set and verify its current status and exact resource changes.
- Revalidate account, region, VPC, subnet IDs and AZ mappings.
- Revalidate the public route table's Internet Gateway route.
- Confirm data-subnet associations and data routes are unchanged.
- Confirm the approved test start time, end time, test actions and stop criteria.
- Confirm a cleanup operator and rollback procedure are available.
- Record the approved fixed-cost allowance and acknowledge that data processing,
  transfer and unrelated resources are additional charges.
- Stop if the live state differs from the reviewed baseline or unexpected
  changes appear in the change set.

## 5. Execution and validation — only after approval

1. Execute only the reviewed change set.
2. Wait for stack operations to finish; inspect stack events and resource status.
3. Verify both NAT Gateways are available and located in their intended public
   subnets and Availability Zones.
4. Verify each public subnet has the expected active Internet Gateway route.
5. Verify App-A's dedicated route table has 0.0.0.0/0 pointing to NAT-A.
6. Verify App-B's dedicated route table has 0.0.0.0/0 pointing to NAT-B.
7. Verify each application subnet is associated with its intended route table.
8. Run bounded outbound connectivity tests independently from each AZ using
   approved temporary test workloads and synthetic data only.
9. Record the test target, timestamp, AZ, result and relevant logs.
10. Conduct the approved failure scenario only if its scope and recovery method
    have been explicitly reviewed.
11. Do not claim resilience based on route configuration alone; retain observed
    test results and limitations.

## 6. Cost and stop conditions

Planning estimate for fixed hourly components:
- Two NAT Gateways plus two public IPv4 addresses: approximately $0.10/hour
  under the recorded pricing assumptions.
- Four-hour fixed-cost estimate: approximately $0.40.
- Data processing, transfer and other billable resources are excluded.
- The $1.00 internal planning allowance is not an AWS billing cap.

Stop new test activity if the approved window expires, unexpected costs or
resources appear, the routing baseline is violated, or validation cannot
continue safely. Begin the approved cleanup procedure.

## 7. Rollback and restoration

1. Stop test traffic and temporary workloads.
2. Remove the deployed S3-01 resources through the reviewed teardown procedure.
3. Wait for NAT Gateway deletion to complete before assessing associated
   Elastic IP release; verify allocations rather than assuming deletion succeeded.
4. Re-read both application subnet route-table associations.
5. If an app subnet is not associated with the original shared application
   route table [APP_ROUTE_TABLE_ID], verify its live mapping and explicitly
   restore the original association when safe and approved.
6. Verify the public route table still has its active Internet Gateway default route.
7. Verify both data subnets remain associated with [DATA_ROUTE_TABLE_ID] and
   that its routes are unchanged.
8. Verify the main route table remains unchanged.
9. Re-query NAT Gateways and Elastic IP allocations in us-east-1.
10. Record final stack status, route-table state, cleanup results, outstanding
    resources and any billing uncertainty.

Deleting the stack must not be assumed to restore the original app subnet
associations automatically. Verify the live state explicitly.

## 8. Completion evidence

Retain:
- Before/after route-table and subnet-association outputs.
- Change-set and stack event/resource outputs.
- NAT Gateway and Elastic IP cleanup verification.
- Egress test results from each AZ.
- Failure-scenario results and limitations.
- Actual test duration and cost review.
- Rollback/restoration verification.

Update the Stage 3 traceability matrix only after the acceptance criteria are
supported by observed implementation and test evidence.

## 9. Current decision

**NOT AUTHORIZED FOR EXECUTION.**

This document is a draft plan. It does not grant permission to execute the
change set, delete the stack, modify routes, or create AWS resources.
