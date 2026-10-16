# AWS Account Security Baseline

Date: 29 September 2026

## Verified controls

- AWS customer verification completed.
- AWS Free Plan active.
- Root user MFA enabled.
- Root user has no active access keys.
- Account contact information matches the registered information.

## Evidence

The AWS console dashboard was inspected after account activation.

Raw screenshot is retained locally under:
`evidence/raw/2026-09-29-root-security-dashboard.png`

The raw screenshot is not committed to Git.

## Security decision

Root credentials are reserved for tasks that require root access.
Everyday AWS administration will use a separate administrative identity.