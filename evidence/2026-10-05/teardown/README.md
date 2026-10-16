# Stage 1 Learning Lab Teardown Evidence

Date: 2026-10-05
Project: MedFlow Claims
Stage: 1 — Learning Lab
Region: us-east-1

## Teardown decision

The temporary Stage 1 workload was torn down after implementation and validation were completed.

The reusable foundational VPC/networking and IAM resources were intentionally retained for a future rebuild.

## Workload resources removed

### Application Load Balancer
- `MedFlow-ALB` deleted
- `MedFlow-App-TG` deleted

### Compute
- `MedFlow-App-A-01` terminated
- Final verification showed EC2 state `terminated`
- No running, pending, stopping, or stopped instances remained in the audit query

### Database
- `medflow-claims-db` deleted
- Final verification returned `DBInstanceNotFound`
- Final snapshot was intentionally skipped for this Learning Lab teardown
- Automated backups were requested for deletion during DB removal

### NAT Gateway and public IPv4 address
- Stage 1 NAT Gateway deleted
- Application route `0.0.0.0/0` to the NAT Gateway removed before NAT deletion
- NAT Gateway reached `deleted`
- NAT-associated network interface disappeared
- Elastic IP became disassociated
- Elastic IP allocation was explicitly released
- Final EIP audit returned `InvalidAllocationID.NotFound`

### Claims S3 bucket
- Synthetic test object `sample-claim.txt` deleted
- Bucket was confirmed empty
- `medflow-claims-raw-[AWS_ACCOUNT_ID_REDACTED]-20261005` deleted
- Final `head-bucket` check returned HTTP 404 / Not Found
- Bucket versioning was `None`; no version cleanup was required

### CloudTrail
- `MedFlow-CloudTrail` logging stopped
- Final delivery completed with no reported delivery error
- Additional CloudTrail log and digest files were delivered after the infrastructure teardown
- CloudTrail trail deleted
- Final `get-trail` check returned `TrailNotFoundException`
- CloudTrail S3 log bucket was emptied
- CloudTrail S3 log bucket deleted
- Final `head-bucket` check returned HTTP 404 / Not Found

## Final resource audit

The final `us-east-1` audit returned no matching resources for:
- Running/pending/stopping/stopped EC2 instances
- RDS DB instances
- Available/pending/deleting NAT Gateways
- Application Load Balancers
- Elastic IP allocations
- Unattached EBS volumes

## Retained foundation

The following foundational resources were intentionally retained for future lab rebuilds:
- VPC
- Subnets
- Route tables
- Internet Gateway
- Security Groups
- NACLs
- IAM role/profile
- DB subnet group

The retained foundation is part of the Learning Lab design and avoids rebuilding the base topology for every session.

## Cost checkpoint after teardown

The budget report was checked after teardown. Billing data may lag actual resource activity, so this snapshot is not treated as proof that no charges were incurred.

## Security handling

The repository does not contain:
- passwords
- access keys
- recovery codes
- authentication tokens
- private keys or certificates
- payment information
- raw CloudTrail log files

CloudTrail logs existed temporarily in the AWS S3 destination for validation and were removed during teardown.

## Teardown result

Stage 1 workload teardown: COMPLETE

Cost-bearing application resources: REMOVED

CloudTrail audit infrastructure: REMOVED

Reusable foundation: RETAINED

Repository evidence: PENDING COMMIT

Next action:
Commit and push this teardown evidence, then leave the AWS workload in the cleaned state until the next deliberate lab session.
