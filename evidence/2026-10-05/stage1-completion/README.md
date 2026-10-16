# Stage 1 Completion Evidence

Date: 2026-10-05
Project: MedFlow Claims
Stage: 1 — Learning Lab
Region: us-east-1

## Completion decision

Stage 1 implementation and validation are COMPLETE for the current Learning Lab scope.

Route 53 public DNS is intentionally deferred because no controlled domain is currently available.

This is a documented design decision, not an implementation failure.

## Validated architecture

### Networking

- VPC CIDR: `10.0.0.0/16`
- Two Availability Zones
- Public, private application, and private data subnets
- Internet Gateway attached to the VPC
- Public route table uses the Internet Gateway
- Application route table uses the single Stage 1 NAT Gateway
- Data route table has local VPC routing only
- Application subnets are not publicly addressed
- Data tier has no Internet Gateway route
- Application-to-data access is restricted to required database traffic
- NACL and Security Group controls were validated

Final application route-table validation:
- `0.0.0.0/0` -> NAT Gateway
- Route state: `active`
- Both application subnets associated with the application route table

### Compute

- EC2 application instance deployed in a private subnet
- No public IPv4 address
- IMDSv2 required
- AWS Systems Manager Session Manager validated
- Nginx running successfully
- ALB target health: healthy
- Application returned HTTP 200 through the ALB
- No inbound SSH requirement was introduced

### Storage

S3 raw-claims bucket:
`medflow-claims-raw-[AWS_ACCOUNT_ID_REDACTED]-20261005`

Validated:
- Bucket Owner Enforced
- All four S3 Block Public Access controls enabled
- SSE-S3 (`AES256`)
- Synthetic object upload/download integrity test passed
- No real medical records or PHI uploaded

### Database

RDS:
`medflow-claims-db`

Validated:
- PostgreSQL 18.6
- `db.t3.micro`
- 20 GiB gp3
- Single-AZ
- Private
- Storage encrypted
- Backup retention: 1 day
- Auto minor version upgrade enabled
- Performance Insights disabled
- RDS Extended Support explicitly disabled
- Application-to-database TCP 5432 connectivity succeeded
- PostgreSQL connection used TLS
- PostgreSQL version and database identity validated

### Observability

CloudWatch:
- EC2 `CPUUtilization` metrics available
- Standard monitoring baseline validated

CloudTrail:
- Trail: `MedFlow-CloudTrail`
- Single-Region
- Global service events enabled
- Log-file validation enabled
- Logging enabled
- Actual log files delivered to S3
- Digest files delivered to S3
- No reported delivery or digest errors
- One log file inspected successfully
- `validate-logs` returned `1/1 digest files valid` for the available validation window
- CloudTrail data events and Insights were intentionally not enabled

### DNS

Route 53 public hosted zone:
- Deferred by decision

Reason:
- No controlled domain available for the learner to administer

Validated alternative:
- ALB AWS-provided DNS name successfully served the Stage 1 application

## Evidence repository

Stage 1 evidence committed to the private GitHub repository includes:

- Compute validation
- Storage and database validation
- CloudTrail validation
- Route 53 deferral decision
- This Stage 1 completion record

The repository is intentionally sanitized and does not contain passwords, access keys, recovery codes, private keys, certificates, payment information, or raw CloudTrail logs.

## Cost state at completion review

At the final review:
- AWS Free Plan: ACTIVE
- Remaining credits: 140 USD
- Budget actual reported: 0 USD
- Budget guardrail: present

The following temporary cost-bearing resources remain active for the session:
- EC2
- RDS
- NAT Gateway
- Application Load Balancer
- S3 storage
- CloudTrail/S3 logging

The Learning Lab is designed for teardown between sessions.

## Stage 1 result

Implementation: COMPLETE

Validation: COMPLETE

Route 53: DEFERRED BY DECISION

Teardown: PENDING

Next action:
Review and execute the controlled Learning Lab teardown before ending the session.
