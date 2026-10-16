# Security Rules for AWS-Practice-Lab

This repository is used as a learning and proof-of-work record for the MedFlow AWS SAA-C03 project.

## Never commit

Do not commit:

- passwords
- MFA seeds or QR codes
- recovery codes
- AWS access keys or secret access keys
- session tokens
- API tokens
- private keys or certificates
- database passwords
- `.env` files containing secrets
- payment information
- unredacted personal information
- unredacted AWS account/security information

## Evidence handling

- Raw screenshots and exports go under `evidence/raw/` and must remain untracked.
- Only reviewed and sanitized evidence may be committed.
- Remove secrets and sensitive information before publishing or committing evidence.
- Verify staged changes before every commit.

## Credential handling

Credentials belong in an appropriate password manager or secrets-management system, not in source files or Git history.

If a secret is accidentally committed, treat it as compromised. Revoke or rotate it first, then remove the secret from the repository history.

## Change discipline

For security-sensitive changes:

1. Inspect the current state.
2. Make the smallest necessary change.
3. Verify the result.
4. Review the exact staged diff.
5. Commit only the intended files.

## Repository status

This repository is a learning portfolio. Before publishing changes, review the complete proposed file set and Git history for credentials, account-specific identifiers, private evidence, and personal information. Keep raw evidence and recovery material private. If a credential is exposed, revoke or rotate it before cleaning repository history.
