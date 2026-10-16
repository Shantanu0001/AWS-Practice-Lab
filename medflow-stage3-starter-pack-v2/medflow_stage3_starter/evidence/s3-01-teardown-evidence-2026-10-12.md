# S3-01 Teardown Evidence

**Date:** 2026-10-12
**AWS account:** [AWS_ACCOUNT_ID_REDACTED]
**Region:** us-east-1
**Profile:** local-profile
**Stack:** medflow-stage3-s3-01-network-egress

## Outcome

- CloudFormation stack deletion waiter completed successfully.
- Subsequent stack lookup returned stack-not-found, as expected after deletion.
- Both NAT Gateways reported state `deleted`:
  - `[NAT_GATEWAY_A_ID_REDACTED]`
  - `[NAT_GATEWAY_B_ID_REDACTED]`
- Filtered Elastic IP lookup for the two original allocation IDs returned an empty array.
- Both app subnets were explicitly restored to original route table `[APP_ROUTE_TABLE_ID_REDACTED]`:
  - `[APP_SUBNET_A_ID_REDACTED]`
  - `[APP_SUBNET_B_ID_REDACTED]`
- The restored shared route table contains only the VPC-local route `10.0.0.0/16`.
- Final VPC route-table inventory showed the four original route tables.
- Public subnets retain the Internet Gateway default route.
- Data subnets remain associated with their existing local-only route table.

## Acceptance status

**Deployed and torn down; acceptance testing pending.**

Egress from both application AZs and the planned failure scenario were not tested. This evidence does not establish S3-01 as implemented.

## Evidence references

Pre-teardown CLI transcript:
`s3-01-pre-teardown-20261012-102629.txt`

The CLI output in the project conversation provides the observed deletion, restoration, and final audit results.
