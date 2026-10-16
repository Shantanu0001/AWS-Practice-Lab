# Stage 1 Networking — MedFlow Claims

**Project:** MedFlow Claims — AWS SAA-C03 Capstone
**Repository:** `AWS-Practice-Lab`
**Stage:** 1 — Learning Lab
**Date:** 1 October 2026
**AWS Region:** `us-east-1`
**Status:** Network foundation and routing configuration completed and verified

---

## 1. Purpose

This document records the implementation and verification of the Stage 1 networking foundation for the MedFlow Claims project.

The objective is to build a logically separated VPC network with public, application, and data subnets across two Availability Zones.

The network is being built incrementally, with each resource created and verified before proceeding to the next step. The implementation is intended to provide practical AWS networking experience while keeping the Learning Lab within its cost and security boundaries.

This document records the actual configuration and work completed on 1 October 2026. It also preserves the configuration error encountered during the Public A route-table association and the steps taken to correct it.

## 2. Scope

The completed networking work includes:

- VPC creation
- VPC DNS support and DNS hostnames
- Six IPv4 subnets across two Availability Zones
- Internet Gateway creation and attachment
- Public route table creation
- Public default route creation
- Public subnet associations
- Application route table creation and associations
- Data route table creation and associations
- Route-table inventory and verification
- Confirmation that private tiers do not use the public route table
- Confirmation that the main route table has no Internet Gateway default route
- Documentation of the Public A association correction

The following components are not yet part of this completed networking milestone:

- Security groups
- Custom network ACLs
- NAT Gateway
- EC2 instances
- Application Load Balancer
- RDS
- VPC endpoints
- Network Firewall
- IPv6 configuration

These components will be addressed in later project steps where appropriate.

## 3. Architecture Overview

The Stage 1 network uses one VPC across two Availability Zones.

| Component | Configuration |
|---|---|
| Region | `us-east-1` |
| Availability Zones | `us-east-1a`, `us-east-1b` |
| VPC CIDR | `10.0.0.0/16` |
| Address family | IPv4 |
| Subnets | 6 |
| Public subnets | 2 |
| Application subnets | 2 |
| Data subnets | 2 |
| Internet Gateway | 1 |
| Custom route tables | 3 |
| NAT Gateway | Deferred |
| IPv6 | Deferred |

### Logical architecture

```text
                         Internet
                            |
                            |
                 MedFlow-Stage1-IGW
                            |
                            |
                 MedFlow-Public-RT
                            |
               +------------+------------+
               |                         |
               |                         |
          Public A                    Public B
          10.0.1.0/24                 10.0.2.0/24
          us-east-1a                  us-east-1b


                 MedFlow-App-RT
                            |
               +------------+------------+
               |                         |
               |                         |
            App A                      App B
          10.0.11.0/24                10.0.12.0/24
          us-east-1a                  us-east-1b


                MedFlow-Data-RT
                            |
               +------------+------------+
               |                         |
               |                         |
            Data A                     Data B
          10.0.21.0/24                10.0.22.0/24
          us-east-1a                  us-east-1b
```

The public, application, and data tiers have separate route tables. Only the public route table contains an IPv4 default route to the Internet Gateway.

The application and data route tables contain only the local VPC route at this stage.

## 4. VPC Configuration

### 4.1 VPC details

| Property | Value |
|---|---|
| Name | `MedFlow-Stage1-VPC` |
| VPC ID | `[VPC_ID_REDACTED]` |
| CIDR | `10.0.0.0/16` |
| Region | `us-east-1` |
| State | `available` |
| DNS support | Enabled |
| DNS hostnames | Enabled |

### 4.2 Existing default VPC

Before creating the MedFlow VPC, the account was inspected and an existing default VPC was found.

| Property | Value |
|---|---|
| CIDR | `172.31.0.0/16` |
| Type | Default VPC |
| State | `available` |

The MedFlow VPC uses `10.0.0.0/16`, which does not overlap with the existing default VPC CIDR.

The default VPC was left unchanged.

### 4.3 VPC verification

The VPC was created successfully and its state and CIDR were verified.

DNS support and DNS hostnames were enabled and independently verified.

**Result:** Successful.

## 5. Availability Zones

The account's available Availability Zones were inspected in `us-east-1`.

The project uses the following two zones:

| Project label | Availability Zone | AZ ID |
|---|---|---|
| AZ-A | `us-east-1a` | `use1-az1` |
| AZ-B | `us-east-1b` | `use1-az2` |

The two zones are used to distribute the public, application, and data subnets.

The AZ names and IDs were checked against the account's available-zone response.

## 6. Subnet Design

Six subnets were created in the MedFlow VPC.

| Tier | Subnet name | CIDR | Availability Zone |
|---|---|---|---|
| Public | `MedFlow-Public-A` | `10.0.1.0/24` | `us-east-1a` |
| Public | `MedFlow-Public-B` | `10.0.2.0/24` | `us-east-1b` |
| Application | `MedFlow-App-A` | `10.0.11.0/24` | `us-east-1a` |
| Application | `MedFlow-App-B` | `10.0.12.0/24` | `us-east-1b` |
| Data | `MedFlow-Data-A` | `10.0.21.0/24` | `us-east-1a` |
| Data | `MedFlow-Data-B` | `10.0.22.0/24` | `us-east-1b` |

### 6.1 Subnet IDs

| Subnet | Subnet ID |
|---|---|
| `MedFlow-Public-A` | `[PUBLIC_SUBNET_A_ID_REDACTED]` |
| `MedFlow-Public-B` | `[PUBLIC_SUBNET_B_ID_REDACTED]` |
| `MedFlow-App-A` | `[APP_SUBNET_A_ID_REDACTED]` |
| `MedFlow-App-B` | `[APP_SUBNET_B_ID_REDACTED]` |
| `MedFlow-Data-A` | `[DATA_SUBNET_A_ID_REDACTED]` |
| `MedFlow-Data-B` | `[DATA_SUBNET_B_ID_REDACTED]` |

### 6.2 Subnet creation and verification

All six subnets were created successfully.

Each subnet was checked for its expected:

- Subnet ID
- CIDR block
- Availability Zone
- VPC association
- Name tag
- Project tags

The subnet inventory was also checked after creation.

**Result:** All six subnet creations and individual verifications succeeded.

## 7. Resource Tagging

The networking resources use the following project tags:

| Tag key | Value |
|---|---|
| `project` | `medflow` |
| `stage` | `1` |
| `lifecycle` | `lab-session` |
| `Name` | Resource-specific name |

The `Name` tag identifies the resource, while the other tags identify its project, stage, and intended lifecycle.

Tags were verified on the VPC, subnets, Internet Gateway, and custom route tables as applicable.

## 8. Internet Gateway

### 8.1 Configuration

| Property | Value |
|---|---|
| Name | `MedFlow-Stage1-IGW` |
| Internet Gateway ID | `[AWS_RESOURCE_ID_REDACTED]` |
| VPC | `[VPC_ID_REDACTED]` |
| Attachment | Successful |

The Internet Gateway was created and attached to the MedFlow VPC.

### 8.2 Verification

The following operations were completed successfully:

- Internet Gateway creation
- Internet Gateway inspection
- Attachment to the MedFlow VPC
- Attachment verification
- Confirmation that no public default route existed before the public route was created

**Result:** Successful.

An Internet Gateway being attached to a VPC does not, by itself, make every subnet public. The route-table configuration and subnet association determine which subnets have a route to it.

## 9. Route Table Design

The VPC now has four route tables:

1. The VPC main route table
2. `MedFlow-Public-RT`
3. `MedFlow-App-RT`
4. `MedFlow-Data-RT`

The three custom route tables provide explicit routing boundaries for the project tiers.

### 9.1 Main route table

| Property | Value |
|---|---|
| Route table ID | `[MAIN_ROUTE_TABLE_ID_REDACTED]` |
| Type | VPC main route table |
| Routes | Local VPC route only |

Route:

```text
10.0.0.0/16 -> local
```

The main route table has no Internet Gateway default route.

The App and Data subnets initially had no explicit route-table associations. They therefore used the main route table until their respective custom route tables were created and associated.

The main route table was inspected again after the custom associations were completed. It remained limited to the local VPC route.

### 9.2 Public route table

| Property | Value |
|---|---|
| Name | `MedFlow-Public-RT` |
| Route table ID | `[PUBLIC_ROUTE_TABLE_ID_REDACTED]` |
| Associated subnets | Public A and Public B |

Routes:

```text
10.0.0.0/16 -> local
0.0.0.0/0   -> [AWS_RESOURCE_ID_REDACTED]
```

The public route table was created with the project tags.

The local route was present after creation. The IPv4 default route to the Internet Gateway was then added and verified.

The route was confirmed to be active and to target the intended Internet Gateway.

### 9.3 Application route table

| Property | Value |
|---|---|
| Name | `MedFlow-App-RT` |
| Route table ID | `[APP_ROUTE_TABLE_ID_REDACTED]` |
| Associated subnets | App A and App B |

Route:

```text
10.0.0.0/16 -> local
```

The route table was created with the required project tags.

It was verified before any subnet associations were made. The initial association list was empty, and the route list contained only the local VPC route.

App A and App B were then associated with this route table and verified individually.

No Internet Gateway or NAT route was added.

### 9.4 Data route table

| Property | Value |
|---|---|
| Name | `MedFlow-Data-RT` |
| Route table ID | `[DATA_ROUTE_TABLE_ID_REDACTED]` |
| Associated subnets | Data A and Data B |

Route:

```text
10.0.0.0/16 -> local
```

The route table was created with the required project tags.

It was verified before subnet associations. The initial association list was empty, and the route list contained only the local VPC route.

Data A and Data B were then associated with this route table and verified individually.

No Internet Gateway or NAT route was added.

## 10. Final Subnet-to-Route-Table Associations

The final intended associations are:

| Subnet | Subnet ID | Route table | Route table ID | Association |
|---|---|---|---|---|
| Public A | `[PUBLIC_SUBNET_A_ID_REDACTED]` | `MedFlow-Public-RT` | `[PUBLIC_ROUTE_TABLE_ID_REDACTED]` | Associated |
| Public B | `[PUBLIC_SUBNET_B_ID_REDACTED]` | `MedFlow-Public-RT` | `[PUBLIC_ROUTE_TABLE_ID_REDACTED]` | Associated |
| App A | `[APP_SUBNET_A_ID_REDACTED]` | `MedFlow-App-RT` | `[APP_ROUTE_TABLE_ID_REDACTED]` | Associated |
| App B | `[APP_SUBNET_B_ID_REDACTED]` | `MedFlow-App-RT` | `[APP_ROUTE_TABLE_ID_REDACTED]` | Associated |
| Data A | `[DATA_SUBNET_A_ID_REDACTED]` | `MedFlow-Data-RT` | `[DATA_ROUTE_TABLE_ID_REDACTED]` | Associated |
| Data B | `[DATA_SUBNET_B_ID_REDACTED]` | `MedFlow-Data-RT` | `[DATA_ROUTE_TABLE_ID_REDACTED]` | Associated |

All six subnets have explicit associations with their intended custom route tables.

The custom route tables were verified to have `Main=False` for their subnet associations, and the associations were in the `associated` state.

## 11. Routing Verification

The final routing audit inspected all route tables in the VPC and checked the individual custom route tables.

### 11.1 Public routing

Verified:

- Public A is associated with `MedFlow-Public-RT`.
- Public B is associated with `MedFlow-Public-RT`.
- The public route table contains the local VPC route.
- The public route table contains the IPv4 default route to the intended Internet Gateway.
- The default route is active.

### 11.2 Application routing

Verified:

- App A is associated with `MedFlow-App-RT`.
- App B is associated with `MedFlow-App-RT`.
- The application route table contains the local VPC route.
- The application route table has no IPv4 default route to the Internet Gateway.
- No NAT route is configured.

### 11.3 Data routing

Verified:

- Data A is associated with `MedFlow-Data-RT`.
- Data B is associated with `MedFlow-Data-RT`.
- The data route table contains the local VPC route.
- The data route table has no IPv4 default route to the Internet Gateway.
- No NAT route is configured.

### 11.4 Main route table

Verified:

- The main route table was identified using the main-association filter.
- It contains the local VPC route.
- It has no Internet Gateway default route.

### 11.5 Final routing invariant

The completed configuration satisfies this routing invariant:

```text
Only MedFlow-Public-RT contains:

0.0.0.0/0 -> [AWS_RESOURCE_ID_REDACTED]
```

The App and Data route tables contain only:

```text
10.0.0.0/16 -> local
```

The main route table also contains only the local route.

The final all-route-table inventory and individual route-table inspections confirmed the intended configuration.

**Result:** Routing audit successful.

## 12. Troubleshooting Record — Public A Association

### 12.1 Initial issue

During the Public A association step, the wrong route-table ID was used.

The subnet was initially associated with the VPC main route table:

```text
Route table:
[MAIN_ROUTE_TABLE_ID_REDACTED]
```

instead of the intended custom public route table:

```text
MedFlow-Public-RT
[PUBLIC_ROUTE_TABLE_ID_REDACTED]
```

The initial association was:

```text
[ASSOCIATION_ID_REDACTED]
```

### 12.2 Detection

The issue was detected during route-table association verification.

The inspection showed that Public A was associated with the main route table, which contained only the local VPC route.

Therefore, Public A was not yet using the intended public default route.

### 12.3 Correction

The incorrect association was replaced using the AWS CLI operation:

```powershell
aws ec2 replace-route-table-association `
  --profile local-profile `
  --region us-east-1 `
  --association-id [ASSOCIATION_ID_REDACTED] `
  Illustrative command fragment (not directly executable):
  --route-table-id <REDACTED_PUBLIC_ROUTE_TABLE_ID>
```

AWS returned the new association ID:

```text
[ASSOCIATION_ID_REDACTED]
```

The association state was reported as `associated`.

### 12.4 Post-correction verification

The subnet-to-route-table query was repeated.

It confirmed that Public A was now associated with:

```text
[PUBLIC_ROUTE_TABLE_ID_REDACTED]
```

The effective routes were:

```text
10.0.0.0/16 -> local
0.0.0.0/0   -> [AWS_RESOURCE_ID_REDACTED]
```

Both routes were active.

### 12.5 Outcome

The association correction succeeded.

No application workload was running in the subnet at the time of the correction.

The error and recovery are retained in the project record as a genuine troubleshooting event.

## 13. Cost and Resource Decisions

This is a zero-budget-focused Learning Lab. Resource choices are being made with cost awareness, and cost-bearing resources are deferred until they are needed and their costs have been reviewed.

### 13.1 NAT Gateway

A NAT Gateway has deliberately not been created.

The current application and data route tables have no default route to a NAT Gateway.

This avoids introducing a resource with hourly and data-processing charges during the network foundation stage.

The absence of NAT means private subnets do not currently have general outbound IPv4 Internet access through a NAT Gateway.

This is an intentional intermediate configuration, not a completed outbound-connectivity design.

### 13.2 Other resources

No EC2 instances, RDS instances, load balancers, or other application workloads were created as part of this routing milestone.

The network foundation is being completed and verified before application resources are introduced.

### 13.3 Cost boundary

The existence of a VPC and route tables does not mean that all possible VPC-related resources are free. Future resources must be assessed individually before deployment.

A budget notification is an alerting control, not a guaranteed spending cap.

## 14. Security Considerations

The current routing configuration provides network-level separation between the three tiers.

### Public tier

The public subnets use a route table with a default route to the Internet Gateway.

This routing configuration alone does not establish that any instance is safely exposed. Security groups, network ACLs, public IP assignment, and workload configuration must also be considered before deploying public-facing resources.

### Application tier

The application subnets use a separate route table containing only the local VPC route.

They do not use the public route table and do not currently have a NAT route.

### Data tier

The data subnets use a separate route table containing only the local VPC route.

The data tier has no direct Internet Gateway route.

This is a required design property for the project and will be checked again if routing changes are made later.

### Limitations of the current milestone

Route-table separation is not a replacement for security groups or network ACLs.

The current configuration does not yet prove application-to-database access restrictions because those resources and rules have not been implemented.

The network foundation should therefore be considered routing-complete, not application-security-complete.

## 15. Evidence and Reproducibility

The networking work was performed through the AWS CLI in Windows PowerShell using the `local-profile` profile and the `us-east-1` Region.

The process used a step-by-step approach:

1. Inspect existing resources.
2. Create one resource.
3. Verify the resource.
4. Apply the required configuration.
5. Verify the resulting state.
6. Continue only after successful verification.

The completed checks included:

- VPC inventory and verification
- DNS support and hostname verification
- Subnet inventory
- Subnet tag verification
- Internet Gateway verification
- Internet Gateway attachment verification
- Route-table inventory
- Route-table route inspection
- Subnet association verification
- Effective-route verification
- Main route table inspection
- Full routing audit

The Public A association error and correction were retained as part of the troubleshooting history.

Raw screenshots and other sensitive evidence should remain in the ignored `evidence/raw/` directory. Only sanitized, appropriate evidence should be committed to the repository.

Before committing, review the staged diff and ensure it contains no credentials, tokens, private keys, account-sensitive information, or unredacted sensitive data.

## 16. Completion Summary

| Task | Result |
|---|---|
| VPC creation | Successful |
| VPC verification | Successful |
| DNS support | Enabled and verified |
| DNS hostnames | Enabled and verified |
| Public A creation | Successful |
| Public B creation | Successful |
| App A creation | Successful |
| App B creation | Successful |
| Data A creation | Successful |
| Data B creation | Successful |
| Subnet inventory | Successful |
| Subnet tags | Verified |
| Internet Gateway creation | Successful |
| Internet Gateway attachment | Successful |
| Public route table | Created and verified |
| Public default route | Created and verified |
| Public A association | Corrected and verified |
| Public B association | Successful and verified |
| App route table | Created and verified |
| App A association | Successful and verified |
| App B association | Successful and verified |
| Data route table | Created and verified |
| Data A association | Successful and verified |
| Data B association | Successful and verified |
| Main route table | Local route only |
| App route table | Local route only |
| Data route table | Local route only |
| Public route table | Local route and IGW default route |
| Full routing audit | Successful |

## 17. Current State and Next Steps

The Stage 1 VPC routing foundation is complete.

The current network contains:

- One VPC
- Six subnets across two Availability Zones
- One attached Internet Gateway
- One public route table
- One application route table
- One data route table
- One unchanged main route table

The public subnets are explicitly associated with the public route table. The application and data subnets are explicitly associated with their respective private route tables.

The next project phase is to design and implement the network security controls, beginning with security groups. The rules should be defined and reviewed before creating workloads that depend on them.

Planned future work includes:

1. Define the security-group model and permitted traffic flows.
2. Create and verify the required security groups.
3. Review network ACL requirements and implement them deliberately.
4. Prepare the private application host and its management access.
5. Introduce application and data resources only after reviewing their security and cost implications.
6. Re-verify routing whenever new network resources or routes are introduced.

NAT Gateway remains deferred until a specific requirement justifies its cost and the deployment has been reviewed.

---

**Milestone status:** Stage 1 VPC routing foundation completed and verified on 1 October 2026.

**Important:** This document records the state verified during this milestone. If resources are changed later, update the evidence and record the date and reason for the change rather than silently rewriting historical results.
