# Stage 3 Network Decision — Per-AZ Egress (Revised)

**Decision ID:** ADR-S3-NET-01
**Status:** Proposed; no deployment authorized.

## Evidence that changed the design

The read-only preflight returned:
- Public-A and Public-B are in `us-east-1a` and `us-east-1b` and use an IGW-backed public route table.
- App-A is in `us-east-1a`; App-B is in `us-east-1b`.
- Both app subnets currently share `[AWS_RESOURCE_ID_REDACTED]`.
- No NAT Gateways were returned for the VPC.
- Preflight correctly blocked the original template because a single route table cannot have two competing `0.0.0.0/0` routes.

## Revised proposed design

The revised template creates:
1. A dedicated route table for App-A and one for App-B in the existing VPC.
2. A route-table association from each app subnet to its dedicated route table.
3. One public NAT Gateway and Elastic IP in each existing public subnet.
4. One `0.0.0.0/0` route in each app route table, targeting the NAT Gateway in the same AZ.

Data subnet route tables are not included in this stack and must remain unchanged.

## Important teardown behavior

The app subnets are currently explicitly associated with a pre-existing shared route table (`[AWS_RESOURCE_ID_REDACTED]`). Deleting this stack removes its new subnet associations; AWS then returns those subnets to the VPC's main route table, **not automatically to the old shared custom route table**.

Therefore, before a stack is deleted, record and verify the original mapping. After stack deletion, explicitly re-associate both app subnets with `[AWS_RESOURCE_ID_REDACTED]` (provided a fresh read-only check confirms this is still the intended original mapping). Verify the final associations and route targets. Do not treat stack deletion alone as a complete rollback.

## Cost gate

Two NAT Gateways have hourly and per-GB processing charges; two EIPs may incur public IPv4 charges. Earlier planning estimate: about `$0.10/hour` fixed for two NAT Gateways plus two EIPs, or about `$0.80` for an eight-hour lab before processing/transfer, subject to current rates. This is indicative only. Verify current us-east-1 pricing before deployment and set a time-bounded lab window. The `$1/month` budget is an alert, not a hard spending cap.

## Alternatives
- One zonal NAT shared across AZs: rejected for the target requirement because a NAT AZ failure removes egress for workloads in the other AZ that depend on it.
- Two zonal NAT Gateways: proposed because the project traceability matrix explicitly requires one NAT Gateway per AZ.
- Regional NAT: worth documenting as an alternative, but not a silent substitution for the explicit learning requirement.
- VPC endpoints: useful for justified AWS-service paths, but not a general replacement for public internet egress.

## Acceptance criteria
- Both app subnets use distinct route tables.
- Each app route table's default route points to the NAT Gateway in its own AZ.
- Each NAT Gateway is in the public subnet of that AZ and the public subnet's default route points to the IGW.
- Data route tables are unchanged.
- A bounded egress test succeeds from each app AZ using temporary workloads, followed by verified teardown/rollback.
- Evidence is captured and S3-01 in the traceability matrix is updated only after test results exist.
