# AWS CLI Authentication

Date: 29 September 2026

## Authentication method

AWS CLI v2 was authenticated using browser-based login and a locally configured AWS CLI profile. The local profile name is intentionally not published.

## Verification

- AWS CLI version: 2.37.5
- AWS region: `us-east-1`
- Browser-based AWS login completed successfully.
- MFA-authenticated session completed successfully.
- `aws sts get-caller-identity --profile <local-profile>` succeeded.
- `aws configure list --profile <local-profile>` showed credential source `login`.
- No shared AWS credentials file was present.
- No AWS credential environment variables were present.
- AWS CLI login cache was present.
- STS successfully identified the authenticated principal; its name is omitted from this public record.

## Security decision

The lab does not use long-lived IAM access keys for local AWS CLI authentication.

The CLI login session provides temporary credentials and is managed by the AWS CLI.

## Limitation

The historical learning environment used a bootstrap identity with broad administrative permissions. This was a learning-lab limitation, not a recommended production access model. Workload access should use scoped, least-privilege roles and policies.

## Next milestone

Secure the local development environment and establish the first AWS VPC only after the account, identity, authentication, and cost controls have been verified.
