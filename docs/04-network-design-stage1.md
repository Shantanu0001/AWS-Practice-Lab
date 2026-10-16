# Stage 1 Network Design

Date: 29 September 2026

## Region

`us-east-1`

## Availability Zones

- AZ-A: `us-east-1a` (`use1-az1`)
- AZ-B: `us-east-1b` (`use1-az2`)

## VPC

CIDR: `10.0.0.0/16`

The account already contains the AWS default VPC `172.31.0.0/16`.
The MedFlow VPC CIDR does not overlap with the default VPC.

## Subnets

| Tier | AZ | CIDR |
|---|---|---|
| Public A | us-east-1a | 10.0.1.0/24 |
| Public B | us-east-1b | 10.0.2.0/24 |
| App A | us-east-1a | 10.0.11.0/24 |
| App B | us-east-1b | 10.0.12.0/24 |
| Data A | us-east-1a | 10.0.21.0/24 |
| Data B | us-east-1b | 10.0.22.0/24 |

## Routing model

Public subnets will eventually receive a default route to an Internet Gateway.

Private application and data subnets will not receive a direct Internet Gateway route.

The data tier must never have a direct route to the Internet Gateway.

## Addressing

IPv4 is used for Stage 1.

IPv6 is intentionally deferred.

## Tags

- `project=medflow`
- `stage=1`
- `lifecycle=lab-session`
- `Name` tag identifies the resource

## Cost boundary

The VPC itself has no additional VPC charge.

[DECISION — 2026-10-05] A single public NAT Gateway is deployed for the Stage 1 Learning Lab so private App subnets can reach required outbound services, including AWS Systems Manager.

- NAT Gateway: `[NAT_GATEWAY_ID_REDACTED]`
- Elastic IP allocation: `[AWS_RESOURCE_ID_REDACTED]`
- Public subnet: `[PUBLIC_SUBNET_A_ID_REDACTED]` (`us-east-1a`)
- App route table: `[APP_ROUTE_TABLE_ID_REDACTED]`
- App default route: `0.0.0.0/0 -> [NAT_GATEWAY_ID_REDACTED]`

The NAT Gateway is temporary Learning Lab infrastructure and must be deleted during teardown because it incurs hourly and data-processing charges.

The Data route table remains isolated from both the Internet Gateway and NAT Gateway.

## Deployment sequence

1. Create VPC.
2. Verify VPC.
3. Enable DNS support.
4. Enable DNS hostnames.
5. Create subnets.
6. Create route tables.
7. Create and attach Internet Gateway.
8. Associate public route table with public subnets.
9. Allocate and tag Elastic IP for the Stage 1 NAT Gateway.
10. Create the single public NAT Gateway in Public-A.
11. Wait for the NAT Gateway to become available.
12. Add `0.0.0.0/0 -> NAT Gateway` to the App route table.
13. Verify App-A and App-B use the App route table.
14. Verify the Data route table contains only the local VPC route.
15. Verify private subnet routing does not directly use the Internet Gateway.

## Design decision

This is the Stage 1 Learning Lab network design. It is intentionally smaller than the final production-style architecture and will evolve through later stages.
