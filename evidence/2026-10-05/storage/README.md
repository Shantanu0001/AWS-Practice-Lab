# Stage 1 Storage & Database Evidence

Date: 2026-10-05
Project: MedFlow Claims
Stage: 1 — Learning Lab
Region: us-east-1

## Scope

This evidence records the Stage 1 S3 and Amazon RDS implementation and validation.

The implementation remains aligned with the Learning Lab architecture:
- S3 is used for claim-object storage.
- PostgreSQL RDS is deployed in the private data tier.
- RDS is intentionally Single-AZ for Stage 1.
- The RDS instance is not publicly accessible.
- Database access is restricted through the existing Data security group.

## Amazon S3

Bucket:
`medflow-claims-raw-[AWS_ACCOUNT_ID_REDACTED]-20261005`

Validated configuration:
- Object ownership: `BucketOwnerEnforced`
- Block Public Access:
  - BlockPublicAcls = true
  - IgnorePublicAcls = true
  - BlockPublicPolicy = true
  - RestrictPublicBuckets = true
- Default encryption: SSE-S3 (`AES256`)
- SSE-C: blocked
- Bucket policy: none configured
- Project tags:
  - `project=medflow`
  - `stage=1`
  - `lifecycle=lab-session`

Validation performed:
1. Uploaded synthetic test object `sample-claim.txt`.
2. Confirmed the stored object was encrypted with `AES256`.
3. Downloaded the object back from S3.
4. Compared the SHA-256 hash of the original and downloaded files.
5. Hashes matched exactly.

Synthetic-object validation result:

`551894351B5C9C6CF4E60F03B58E312BB3136DBE270FF520A38574A3F92BA633`

Result: PASS — uploaded and downloaded object content matched.

No real medical records, PHI, patient data, or production claims data were uploaded.

## Amazon RDS for PostgreSQL

DB identifier:
`medflow-claims-db`

Validated configuration:
- Engine: PostgreSQL
- Engine version: `18.6`
- Instance class: `db.t3.micro`
- Storage: `20 GiB gp3`
- Multi-AZ: false
- Publicly accessible: false
- Storage encryption: enabled
- Backup retention: 1 day
- Auto minor version upgrade: enabled
- Performance Insights: disabled
- Enhanced Monitoring interval: 0
- Deletion protection: disabled
- Copy tags to snapshot: enabled
- RDS Extended Support: explicitly disabled
- Port: `5432`
- Database name: `medflowclaims`
- DB subnet group: `medflow-data-subnet-group`
- Security group: `[AWS_RESOURCE_ID_REDACTED]`
- VPC: `[VPC_ID_REDACTED]`

The DB subnet group contains:
- Data-A: `10.0.21.0/24` in `us-east-1a`
- Data-B: `10.0.22.0/24` in `us-east-1b`

This keeps the database in the private data tier. The database has no public endpoint exposure.

## Database security validation

The Data security group was verified before database creation.

Inbound:
- TCP `5432`
- Source: App security group `[AWS_RESOURCE_ID_REDACTED]`
- No direct CIDR-based database ingress

This preserves the intended App -> Data access path.

## Connectivity validation

An interactive AWS Systems Manager session was established to the private EC2 application instance.

From the private EC2 instance:
1. The RDS hostname resolved to a private VPC address.
2. TCP connectivity to port `5432` succeeded.
3. The PostgreSQL client connected successfully using TLS.

Database validation:

`SELECT current_database(), current_user, inet_server_addr(), inet_server_port();`

Result:
- Database: `medflowclaims`
- User: `medflowadmin`
- Server address: private VPC address
- Server port: `5432`

PostgreSQL version validation:

`SELECT version();`

Result:
- PostgreSQL `18.6`

SSL validation:

`SELECT current_setting('ssl') AS ssl_enabled;`

Result:
- `on`

`\conninfo` confirmed:
- SSL connection
- TLSv1.3
- Cipher: TLS_AES_256_GCM_SHA384

Result: PASS — private application-to-database connectivity and encrypted PostgreSQL connectivity were both validated.

## Errors encountered and resolved

### 1. S3 tag JSON encoding issue

PowerShell initially produced an encoding-related error when the S3 tag JSON file was supplied to the AWS CLI.

Resolution:
- Recreated the JSON file as UTF-8 without a BOM.
- Re-ran the command successfully.

### 2. RDS CLI query quoting issue

A PowerShell/JMESPath query containing backticks caused a quoting/parsing problem.

Resolution:
- Removed the unnecessary filter from the diagnostic query.
- Re-ran the command successfully.

### 3. Initial RDS creation rejected

The first RDS creation attempt was rejected because the generated master password contained characters that were invalid for the RDS password requirements.

Resolution:
- Generated a new 24-character password using a compatible character set.
- Stored the password in Bitwarden.
- Created the RDS instance successfully.
- The password itself is intentionally not recorded in this repository.

### 4. Windows PowerShell random-generation compatibility

`RandomNumberGenerator.Fill` was unavailable in the Windows PowerShell environment used for the lab.

Resolution:
- Used `RNGCryptoServiceProvider` instead.
- Generated and validated the replacement password locally.
- Cleared the password variables after use.

### 5. PostgreSQL client not initially installed

The private EC2 instance did not initially contain `psql`.

Resolution:
- Installed the PostgreSQL 15 client package on the EC2 instance.
- Used it only as a client to validate the PostgreSQL 18.6 RDS server.

## Security notes

The following were intentionally not recorded here:
- RDS master password
- AWS access keys
- Recovery codes
- Private keys or certificates
- Payment information
- Authentication tokens

The repository remains a sanitized proof-of-work record.

## Cost notes

RDS is a running, cost-bearing resource.

The Stage 1 Learning Lab currently also contains other cost-bearing resources, including the NAT Gateway and internet-facing ALB. These resources are intentionally temporary and must be considered during teardown.

The RDS configuration was created only after an explicit cost approval for this lab session.

Cost safety actions:
- Resource tags use the project/lifecycle convention.
- RDS is intentionally not protected from deletion.
- Backup retention is limited to 1 day for the lab.
- No Multi-AZ deployment was enabled.
- Performance Insights was not enabled.

## Evidence status

Stage 1 Storage & Database implementation: COMPLETE

Validated:
- S3 bucket security baseline
- S3 encryption
- S3 object round-trip integrity
- RDS private placement
- RDS encryption at rest
- RDS Single-AZ configuration
- Database security-group restriction
- Private application-to-database connectivity
- PostgreSQL TLS connectivity
- PostgreSQL version and database identity

Next phase:
- Continue Stage 1 only after repository evidence is committed and the current cost state is reviewed.
