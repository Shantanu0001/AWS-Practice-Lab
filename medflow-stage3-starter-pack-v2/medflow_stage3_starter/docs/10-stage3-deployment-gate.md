# Stage 3 S3-01 — Deployment Gate

No AWS mutation is authorized by this document.

## Gate 1 — Local repository
- [ ] Review the v2 template and docs.
- [ ] Copy into the repository's intended `infrastructure/stage3` path.
- [ ] Run offline tests.
- [ ] Run `git diff --check` and inspect the diff.
- [ ] Confirm no unrelated files changed.

## Gate 2 — Read-only live-state recheck
- [ ] Confirm the VPC and all four subnet IDs still match the intended VPC.
- [ ] Confirm public subnet AZs match app subnet AZs.
- [ ] Confirm public subnet default routes target an IGW.
- [ ] Confirm app subnets' original association is still `[AWS_RESOURCE_ID_REDACTED]`.
- [ ] Confirm data route tables have not changed and there are no NAT Gateways.
- [ ] Record the VPC main route table ID as well as the original app route table ID.

## Gate 3 — Cost and rollback
- [ ] Verify current NAT Gateway and public IPv4 prices for us-east-1.
- [ ] Set a short test window and a teardown owner/time.
- [ ] Save the original subnet-to-route-table mapping.
- [ ] Prepare and review a teardown sequence that deletes the stack, restores both app subnet associations to the original shared route table, and verifies state.
- [ ] Confirm the data subnets remain untouched.

## Gate 4 — CloudFormation
- [ ] Run `validate-template` (validation only).
- [ ] Create a CloudFormation change set (this creates a change-set record, not the stack resources).
- [ ] Review every resource and replacement/association effect.
- [ ] Do not execute the change set until the user explicitly approves deployment.

## Post-deployment acceptance (only after explicit approval)
- [ ] Confirm stack resources and route associations.
- [ ] Run a bounded egress test per AZ.
- [ ] Capture CLI outputs and test evidence.
- [ ] Tear down NAT/EIP resources within the agreed window.
- [ ] Restore original app subnet associations and verify the final route table mapping.
- [ ] Update S3-01 matrix with actual results, not intended behavior.
