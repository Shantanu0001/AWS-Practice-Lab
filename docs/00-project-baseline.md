# Project Baseline

**Project:** MedFlow Claims AWS SAA-C03 Learning Lab
**Repository:** AWS-Practice-Lab
**Workstation:** Windows / PowerShell
**Last status review:** 12 October 2026

## 1. Historical starting baseline

The original baseline was recorded on 28 September 2026.

At that time, the project documentation stated that the AWS account
had not yet been created and no infrastructure had been deployed.
Those statements describe the historical starting point only; they
must not be used as the current AWS status.

The original baseline also recorded an existing private GitHub
repository and the security practices listed below.

## 2. Current verified project status

The following status is based on project records and command output
reviewed on 12 October 2026.

- Stage 2 has a completion record for bounded learning slices. It
  does not represent a permanent full-platform production deployment.
- Stage 3 S3-01 was temporarily deployed and then torn down.
- The canonical Stage 3 network template passed local structural
  tests, JSON parsing, and AWS CloudFormation template validation.
- The latest AWS inspection found both application subnets associated with the same route table. That route table contained only the VPC-local route.
- The latest NAT Gateway inventory returned no NAT Gateways for the
  inspected VPC.
- S3-01 egress and Availability Zone failure acceptance tests remain
  pending.
- The local Git working tree contains uncommitted and untracked work.
  GitHub's latest server-side state has not been refreshed and verified
  as part of this review.

These observations are time-bounded. Reinspect AWS and Git when a
later decision depends on their current state.

## 3. Cost baseline and authorization

**Default personal cloud budget: INR 0.**

This is the operating restriction unless the project owner explicitly
approves a bounded amount for a specific activity.

- Do not create charge-bearing infrastructure under the default plan.
- AWS budgets and alerts are not hard spending caps.
- Prefer offline validation, local tests, documentation, and read-only
  inspection.
- Obtain explicit approval before any deployment that may incur cost.
- After an approved lab, inspect resource state and applicable billing.
  Billing data may be delayed.

The historical fact that earlier learning slices were run does not
authorize new deployments.

## 4. Security baseline

The original baseline recorded these intended or established practices:

- GitHub account has two-factor authentication enabled.
- GitHub recovery codes are stored in Bitwarden.
- A dedicated Proton Mail account is intended for AWS account use.
- Bitwarden is the password manager.
- Google Authenticator is the planned AWS TOTP authenticator.
- The GitHub repository is private.
- `.gitignore` excludes common credential, key, environment, AWS local
  configuration, state, and raw-evidence paths.
- `SECURITY.md` defines repository security rules.

Items originally described as intended or planned must not be assumed
to have been completed without separate evidence.

Secrets, passwords, recovery codes, private keys, and unredacted
sensitive evidence must remain outside Git.

## 5. Repository and change-control rules

For security-sensitive or infrastructure-related changes:

1. Inspect the current state.
2. Identify the authoritative requirements and relevant evidence.
3. Make the smallest necessary change.
4. Run local validation where possible.
5. Review the exact diff and repository status.
6. Stage only explicitly reviewed files.
7. Commit only after approval.
8. Push only after reviewing the intended commit and remote state.

Do not perform bulk moves, deletions, or consolidation based only on
file names. Preserve backups and evidence until their purpose is known.

## 6. Evidence and status terminology

Use these distinctions consistently:

- **Proposed:** design documented but not implemented.
- **Locally tested:** local tests passed; AWS behavior is not implied.
- **AWS template validated:** CloudFormation accepted the template;
  resources were not created by that validation call.
- **Deployed:** resources were created, with evidence of their state.
- **Validated:** the stated acceptance criteria were actually tested
  and the results were recorded.
- **Torn down:** the temporary resources were removed, supported by
  post-cleanup evidence.
- **Pending validation:** required acceptance tests have not yet passed
  or do not have sufficient evidence.

Do not mark a requirement complete based only on a successful JSON
parse, unit test, template validation, or resource inventory.

## 7. Current next milestone

Stabilize the repository and establish one consistent, evidence-backed
project status before continuing implementation.

The sequence is:

1. Reconcile project entry-point and stage documentation.
2. Review the Stage 3 matrix and supporting evidence.
3. Identify canonical files, duplicates, backups, and local-only work.
4. Verify the selected local application and its tests.
5. Review all proposed repository changes before staging or committing.
6. Continue Stage 3 with local, zero-cost work first.
7. Leave cloud-dependent acceptance tests pending until an explicitly
   approved and bounded test is possible.

## 8. Historical next milestone

The original 28 September 2026 baseline identified secure AWS account
creation and root identity protection as its next milestone. This is
retained as a historical record and is not the current project status.
