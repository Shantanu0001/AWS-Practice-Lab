## Security Groups — 02 October 2026

### Security Group Inventory

| Tier | Name | Security Group ID |
|---|---|---|
| ALB | MedFlow-ALB-SG | [AWS_RESOURCE_ID_REDACTED] |
| App | MedFlow-App-SG | [AWS_RESOURCE_ID_REDACTED] |
| Data | MedFlow-Data-SG | [AWS_RESOURCE_ID_REDACTED] |

### Effective Rules

| Security Group | Direction | Protocol | Port | Source |
|---|---|---|---|---|
| MedFlow-ALB-SG | Inbound | TCP | 80 | 0.0.0.0/0 |
| MedFlow-App-SG | Inbound | TCP | 80 | MedFlow-ALB-SG |
| MedFlow-Data-SG | Inbound | TCP | 5432 | MedFlow-App-SG |

All three groups retain the default outbound IPv4 allow rule.

### Verification

Security-group rules were verified with:

`aws ec2 describe-security-group-rules`

Verified traffic paths:

- Internet → ALB: TCP 80
- ALB → App: TCP 80
- App → Data: TCP 5432

Verified blocked paths by rule absence:

- Internet → App: TCP 80
- Internet → Data: TCP 5432

### Security Notes

The application and database tiers are not directly exposed to the internet.

The data-tier PostgreSQL rule references the application security group rather than a broad CIDR.

No SSH/22 inbound rule was created.

### Evidence

Security-group configuration was created and verified on 02 October 2026.

AWS resource IDs are recorded above for reproducibility.


## Network ACLs — 02 October 2026

### NACL Architecture

The VPC uses two NACLs:

| NACL | ID | Default | Associated Subnets |
|---|---|---|---|
| Default NACL | [AWS_RESOURCE_ID_REDACTED] | Yes | Public-A, Public-B, App-A, App-B |
| MedFlow-Data-NACL | [AWS_RESOURCE_ID_REDACTED] | No | Data-A, Data-B |

### Custom Data NACL Rules

| Direction | Rule | Protocol | Port Range | CIDR | Action |
|---|---:|---|---|---|---|
| Inbound | 100 | TCP | 5432-5432 | 10.0.11.0/24 | ALLOW |
| Inbound | 110 | TCP | 5432-5432 | 10.0.12.0/24 | ALLOW |
| Outbound | 100 | TCP | 1024-65535 | 10.0.11.0/24 | ALLOW |
| Outbound | 110 | TCP | 1024-65535 | 10.0.12.0/24 | ALLOW |
| Inbound | 32767 | ALL | ALL | 0.0.0.0/0 | DENY |
| Outbound | 32767 | ALL | ALL | 0.0.0.0/0 | DENY |

### Association Verification

Data-A:
- Subnet: [DATA_SUBNET_A_ID_REDACTED]
- NACL: [AWS_RESOURCE_ID_REDACTED]
- Association: aclassoc-05aaba04c45b5c86b

Data-B:
- Subnet: [DATA_SUBNET_B_ID_REDACTED]
- NACL: [AWS_RESOURCE_ID_REDACTED]
- Association: aclassoc-04cdae4e33592d2a6

### Verification

The final VPC NACL audit confirmed:

- Public-A and Public-B remain on the default NACL.
- App-A and App-B remain on the default NACL.
- Data-A and Data-B use the custom MedFlow-Data-NACL.
- The custom Data NACL contains the expected PostgreSQL ingress rules and corresponding return-traffic rules.

### Design Intent

The Security Groups provide stateful resource-level filtering.

The custom Data NACL provides stateless subnet-level defense in depth.

The database tier is not given an internet-facing PostgreSQL rule.

### Evidence Date

02 October 2026.