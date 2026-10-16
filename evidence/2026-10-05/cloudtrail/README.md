# Stage 1 CloudTrail Evidence

Date: 2026-10-05
Project: MedFlow Claims
Stage: 1 — Learning Lab
Region: us-east-1

## Scope

This evidence records the Stage 1 CloudTrail management-event audit baseline.

The configuration uses a single-Region CloudTrail trail with log files delivered to a dedicated private S3 bucket.

## CloudTrail trail

Trail:
`MedFlow-CloudTrail`

Validated configuration:
- Home Region: `us-east-1`
- Multi-Region trail: false
- Include global service events: true
- Log file validation: true
- Custom event selectors: false
- Insights selectors: false
- Organization trail: false
- Logging: true
- S3 destination:
  `medflow-cloudtrail-logs-[AWS_ACCOUNT_ID_REDACTED]-20261005`

This is intentionally the minimal Stage 1 management-event configuration.

The following were intentionally not enabled:
- CloudTrail data events
- CloudTrail Insights
- CloudTrail Lake
- CloudWatch Logs integration

## S3 log destination

Bucket:
`medflow-cloudtrail-logs-[AWS_ACCOUNT_ID_REDACTED]-20261005`

Validated configuration:
- Block Public Access: all four controls enabled
- Object ownership: `BucketOwnerEnforced`
- Default encryption: SSE-S3 (`AES256`)
- Bucket policy public status: false
- Project tags:
  - `project=medflow`
  - `stage=1`
  - `lifecycle=lab-session`

The bucket policy grants the CloudTrail service the minimum S3 permissions required for bucket ACL validation and log delivery to the account-specific `AWSLogs` prefix. The policy also restricts access using the specific CloudTrail trail ARN.

## Delivery validation

After logging was started, CloudTrail successfully delivered actual compressed JSON log files to the S3 destination.

Observed log objects were delivered under:

`AWSLogs/[AWS_ACCOUNT_ID_REDACTED]/CloudTrail/us-east-1/2026/10/05/`

Observed digest objects were delivered under:

`AWSLogs/[AWS_ACCOUNT_ID_REDACTED]/CloudTrail-Digest/us-east-1/2026/10/05/`

CloudTrail status validation:
- Logging: true
- Latest delivery timestamp populated
- Latest delivery error: none
- Latest digest timestamp populated
- Latest digest error: none

## Log inspection

One delivered CloudTrail log file was downloaded to the local temporary directory, decompressed, and inspected.

Observed management events included:
- `cloudtrail.amazonaws.com` — `GetTrail`
- `s3.amazonaws.com` — `GetBucketAcl`

The inspection confirmed that the trail was capturing real management activity.

The temporary downloaded log and decompressed file were deleted after inspection.

## Log-file integrity validation

CloudTrail `validate-logs` was run against the trail for:

`2026-10-05T14:10:00Z` through `2026-10-05T14:30:00Z`

Result:

`1/1 digest files valid`

This proves that the digest file available for that validation window was valid.

Important limitation:
- The validated digest covered results only through approximately `2026-10-05T14:13:18Z`.
- The separately inspected sample log was delivered later, around the `14:20Z` delivery period.
- Therefore the later sample log is recorded as successfully delivered and inspected, but it is not claimed here as cryptographically validated by that earlier digest.

A later digest covering the sample log can be used for a subsequent integrity-validation exercise.

## Errors encountered and resolved

### 1. CloudTrail trail did not initially exist

Before trail creation, `get-trail-status` returned `TrailNotFoundException` for `MedFlow-CloudTrail`.

Resolution:
- Created the trail after confirming there was no existing persistent trail.

### 2. S3 encryption JSON parsing failure

The first `put-bucket-encryption` attempt failed because Windows PowerShell altered the inline JSON argument.

Resolution:
- Wrote the encryption configuration as UTF-8 without BOM to a temporary JSON file.
- Applied the configuration using `file://`.
- Verification returned `AES256`.

### 3. Initial CloudTrail bucket policy was incorrect

The first bucket policy used an incomplete `aws:SourceArn` because the account ID variable was empty in the PowerShell session.

Intentionally incomplete example (not a valid trail ARN):

`arn:aws:cloudtrail:us-east-1:/MedFlow-CloudTrail`

This caused `CreateTrail` to fail with:

`InsufficientS3BucketPolicyException`

Resolution:
- Re-read the AWS account ID using STS.
- Reconstructed the complete trail ARN.
- Replaced the bucket policy.
- Verified the policy before retrying trail creation.

Correct trail ARN:

`arn:aws:cloudtrail:us-east-1:[AWS_ACCOUNT_ID_REDACTED]:trail/MedFlow-CloudTrail`

### 4. Initial S3 log location contained only zero-byte prefixes

Immediately after starting logging, only zero-byte prefix objects were visible.

Resolution:
- Waited for CloudTrail delivery.
- Confirmed actual `.json.gz` log files and digest files were subsequently delivered.

## Security notes

The repository intentionally does not contain:
- AWS access keys
- passwords
- recovery codes
- authentication tokens
- private keys or certificates
- payment information

The CloudTrail log sample itself was not committed to the repository.

No CloudTrail data events were enabled, avoiding unnecessary collection and additional cost during Stage 1.

## Cost notes

This is a Learning Lab configuration and is intended to be temporary.

Cost-bearing components currently running separately include:
- EC2
- RDS
- NAT Gateway
- Application Load Balancer
- S3 storage for claims and CloudTrail logs

CloudTrail is configured only for the required Stage 1 management-event baseline. No higher-volume data-event logging or Insights configuration was enabled.

Teardown remains part of the Learning Lab workflow.

## Evidence status

Stage 1 CloudTrail management-event baseline: COMPLETE

Validated:
- Trail configuration
- Logging enabled
- S3 destination
- S3 security baseline
- Actual CloudTrail log delivery
- Actual digest delivery
- Sample log inspection
- Digest integrity validation for the available validation window
- Corrected and validated CloudTrail bucket policy

Next:
- Continue remaining Stage 1 components only after reviewing cost state and current architecture.
