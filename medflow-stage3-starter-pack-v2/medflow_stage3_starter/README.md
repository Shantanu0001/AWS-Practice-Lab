# MedFlow Stage 3 Starter Pack — v2

This is a **local, proposed CloudFormation revision** for Stage 3 requirement S3-01. It has not been deployed and does not authorize AWS changes.

## What changed from v1
- The preflight showed both app subnets use the same existing route table.
- v1 incorrectly required two pre-existing, distinct app route tables and did not create subnet associations.
- v2 creates two dedicated app route tables and explicit subnet associations, then creates one public NAT Gateway/EIP per AZ and adds same-AZ default routes.

## Files
- `templates/stage3-network-egress.json`: complete proposed S3-01 network slice.
- `scripts/inspect-stage3-network.ps1`: read-only topology preflight.
- `scripts/validate-stage3-template.ps1`: calls CloudFormation `validate-template` only.
- `tests/test_network_template.py`: offline structural tests.
- `docs/09-stage3-network-decision.md`: decision and cleanup implications.
- `docs/10-stage3-deployment-gate.md`: exact next gates before any AWS mutation.

## Offline tests
From the directory containing `tests`:
```powershell
python -m unittest discover -s .\tests -p "test_network_template.py" -v
```

## AWS validation only — no deployment
First copy the corrected template into the repo, review `git diff`, run offline tests, then:
```powershell
.\scripts\validate-stage3-template.ps1 -TemplatePath .\infrastructure\stage3\network-egress.json -Profile local-profile -Region us-east-1
```
The template validation command does not deploy resources. Do not create a stack until live topology, cost, teardown, and a change set have been reviewed and explicit approval has been given.
