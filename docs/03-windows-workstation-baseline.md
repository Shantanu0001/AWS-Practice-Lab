# Windows Workstation Security Baseline

Date: 29 September 2026

## AWS CLI

- AWS CLI version: 2.37.5
- AWS CLI executable: `C:\Program Files\Amazon\AWSCLIV2\aws.exe`
- AWS authentication method: `aws login`
- CLI profile: locally configured profile (name omitted from public documentation)
- Credential source: `login`
- Shared AWS credentials file: not present
- AWS credential environment variables: not present
- AWS login cache: present
- STS identity verification: successful

## Windows security controls inspected

- Windows Firewall: enabled for Domain, Private, and Public profiles.
- Microsoft Defender Antivirus: enabled.
- Microsoft Defender real-time protection: enabled.
- Behavior monitoring: enabled.
- Windows Time service: running.
- Time synchronization: successful.
- Time source query: not completed because `w32tm /query /source` returned Access Denied; synchronization status was successfully verified.

## Security decisions

Long-lived AWS access keys are not used for this lab's local CLI authentication.

No AWS credentials, authentication URLs, MFA secrets, recovery codes, or temporary credential contents are stored in this repository.

## Result

Workstation baseline verification completed.
