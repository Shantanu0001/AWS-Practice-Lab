# AWS CLI Authentication Evidence

Date: 29 September 2026

## Verified

- AWS CLI v2 installed: 2.37.5
- Profile: `local-profile`
- Region: `us-east-1`
- Browser authentication: successful
- MFA authentication: successful
- STS identity verification: successful
- Credential source reported by AWS CLI: `login`
- Shared credentials file: not present
- AWS credential environment variables: not present
- AWS login cache: present
- Long-lived IAM access keys intentionally created: none

## Sensitive material

Authentication URLs, temporary credential contents, account identifiers, passwords, MFA material, and recovery information are not stored in this evidence record.

## Conclusion

The local AWS CLI is using the AWS CLI login mechanism with temporary credentials rather than a long-lived access-key pair.
