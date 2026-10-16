# S3-01 Pre-Deployment Review

**Review date:** 2026-10-12
**Scope:** Read-only review of the S3-01 network-egress change set
**AWS account:** [AWS_ACCOUNT_ID_REDACTED]
**Region:** us-east-1
**Stack:** medflow-stage3-s3-01-network-egress
**Change set:** s3-01-review-20261011
**Decision:** Review only; execution is not approved
**Traceability status:** S3-01 remains Not implemented

## Verified findings

- The stack status is `REVIEW_IN_PROGRESS`.
- The change set status is `CREATE_COMPLETE` and execution status is `AVAILABLE`.
- The change-set description says it is not approved for execution.
- The full `describe-change-set` response contains 10 proposed resource additions and no proposed deletions or replacements.
- The change-set `ChangeSetType` field is absent from the full response and was returned as null by filtered queries. The cause is unresolved.
- The local v2 template and the template retrieved from CloudFormation have matching canonical JSON.
- Both templates contain 10 resources and 5 parameters.
- The local template SHA-256 is `FCA8EA6690DCA8CD51242583B846B8DCE7F8EA70BED2AB9DEB81B744CF8CA256`.
- Public-A and App-A are in `us-east-1a`; Public-B and App-B are in `us-east-1b`.
- The public route table is `[PUBLIC_ROUTE_TABLE_ID_REDACTED]`. Both public subnets are associated, and the active default route points to `[INTERNET_GATEWAY_ID_REDACTED]`.
- Both app subnets are currently associated with `[APP_ROUTE_TABLE_ID_REDACTED]`. Its only observed route is the active local route `10.0.0.0/16`.
- The stack-resource listing returned no rows, and the recent stack-event query returned only the stack-level `REVIEW_IN_PROGRESS` event.

## Proposed resources

- `NatEipA`, `NatEipB`
- `NatGatewayA`, `NatGatewayB`
- `AppRouteTableA`, `AppRouteTableB`
- `AppSubnetAssociationA`, `AppSubnetAssociationB`
- `AppDefaultRouteA`, `AppDefaultRouteB`

## Open issues and acceptance gates

1. Investigate or document the missing `ChangeSetType` metadata before deciding whether the review can be closed.
2. Verify current us-east-1 NAT Gateway and public IPv4 pricing and calculate a bounded lab cost estimate.
3. Confirm the test window, monitoring, and teardown owner before deployment.
4. If deployment is later explicitly approved, test egress independently from both app AZs using temporary workloads.
5. Test the planned AZ/failure scenario and record observed behavior.
6. Verify teardown and restore the original app subnet associations if appropriate. Stack deletion alone must not be assumed to restore the old shared route-table associations.
7. Confirm data subnet route tables remain unchanged.
8. Update the traceability matrix only after required implementation and test evidence exists.

## Safety and scope

- This review record documents observations; it does not authorize deployment.
- No change-set execution, stack deletion, or infrastructure mutation was performed as part of this review.
- The absence of stack resources does not establish that the entire AWS account or all regions are free of chargeable resources.

## Follow-up diagnostic — 2026-10-12

- AWS CLI version: `2.37.5` (`C:\Program Files\Amazon\AWSCLIV2\aws.exe`).
- The installed CloudFormation service model includes `ChangeSetType`.
- A focused `describe-change-set --output json` query returned `ChangeSetTypeExists = False`; the field is absent from the parsed response.
- The same response reported `Status = CREATE_COMPLETE` and `ExecutionStatus = AVAILABLE`.
- The cause of the absent field remains unknown. No inference about the change-set type is made from this absence.
- CLI skeleton attempts failed local parameter/model validation and did not resolve the anomaly.
- No change-set execution, stack deletion, or infrastructure mutation was performed.

**Disposition:** Keep this as an open review issue. Do not execute the change set as a diagnostic.

## Pricing review — 2026-10-12

- Region: `us-east-1` (US East, N. Virginia).
- AWS published NAT Gateway rate used for this estimate: `$0.045` per gateway-hour.
- AWS published public IPv4 rate used for this estimate: `$0.005` per address-hour.
- Proposed fixed hourly subtotal: 2 NAT Gateways + 2 public IPv4 addresses = `$0.10/hour`.
- Estimated fixed subtotal for a 4-hour test window: `$0.40`.
- Internal planning allowance for fixed hourly charges: `$1.00`; this is not an AWS billing cap.
- NAT data processing, internet data transfer, other resources, and billing adjustments are excluded from these fixed-cost estimates.
- AWS pricing references:
  - https://aws.amazon.com/vpc/pricing/
  - https://aws.amazon.com/network-firewall/pricing/
- Each partial NAT Gateway-hour is billed as a full hour.
- Deployment remains unauthorized. No AWS resources were created or changed during this pricing review.

**Disposition:** Pricing baseline recorded for planning. Before deployment, confirm the intended test window, cleanup steps, and the actual resources present.

## Follow-up — CloudFormation API documentation clarification — 2026-10-12

- Official AWS `DescribeChangeSet` API documentation was reviewed:
  https://docs.aws.amazon.com/AWSCloudFormation/latest/APIReference/API_DescribeChangeSet.html
- `ChangeSetType` is not listed among the documented `DescribeChangeSet` response elements.
- Therefore, its absence from the describe response is consistent with the documented API schema and should not, by itself, be treated as an anomaly.
- Earlier notes recorded the missing field as unresolved. This clarification supersedes that interpretation; the historical diagnostic notes are retained as a record of the investigation.
- The change set remains review-only and has not been executed. `ExecutionStatus = AVAILABLE` is not deployment approval.
- No AWS resources were created, deleted, or modified during this documentation review.

**Disposition:** Close the missing-field investigation. Continue the S3-01 pre-deployment review without using `ChangeSetType` from `DescribeChangeSet` as a decision criterion.

## Route baseline verification — 2026-10-12

Read-only `describe-route-tables` output confirmed the following active routes before S3-01 deployment:

- Public route table `[PUBLIC_ROUTE_TABLE_ID_REDACTED]`: `10.0.0.0/16 -> local`; `0.0.0.0/0 -> [INTERNET_GATEWAY_ID_REDACTED]`.
- Shared application route table `[APP_ROUTE_TABLE_ID_REDACTED]`: `10.0.0.0/16 -> local` only.
- Data route table `[DATA_ROUTE_TABLE_ID_REDACTED]`: `10.0.0.0/16 -> local` only.
- Main route table `[MAIN_ROUTE_TABLE_ID_REDACTED]`: `10.0.0.0/16 -> local` only.
- All routes returned in this query were active.
- This confirms the route-table baseline at the time of inspection; it does not prove application egress behavior or failure resilience.
- No AWS resources or routes were modified by this inspection.

**Rollback requirement:** After any approved deployment and teardown, re-check both application subnet associations and restore the original shared application route table only if the live mapping requires it. Verify public and data routes remain unchanged.
