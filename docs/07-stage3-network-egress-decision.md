# Stage 3 Network Egress Decision

**Design status:** Proposed; final design acceptance pending
**Deployment history:** Temporarily deployed and subsequently torn down on 12 October 2026
**Acceptance status:** Pending validation; egress and Availability Zone failure tests remain outstanding
**Scope:** MedFlow Learning Lab and Stage 3 network planning
**Region:** us-east-1

## 1. Observed state

Read-only AWS inventory established that:

- The VPC has DNS support and DNS hostnames enabled.
- Public and private subnet pairs exist across two Availability Zones.
- The public route table has an Internet Gateway route.
- App and data route tables currently have only the local VPC route.
- No NAT Gateways or VPC endpoints were returned by the inventory.
- The existing app security group allows all outbound IPv4 traffic.

These observations describe the inspected state, not a live connectivity test.

## 2. Proposed learning slice

Evaluate private EC2 management through Systems Manager Session
Manager without a NAT Gateway.

Initial design candidates:

- One-AZ learning configuration with the required SSM interface
  endpoints, provisioned only for a bounded lab session.
- Two-AZ configuration for later validation of the intended
  Stage 3 resilience design.
- S3 gateway endpoint only if the lab workload requires private
  S3 access.

Do not include the ec2messages endpoint by default until the
SSM Agent compatibility requirement is established.

## 3. Endpoint cost estimate

The AWS PrivateLink pricing page was checked for the interface
endpoint hourly rate in `us-east-1`. The rate used for this estimate
is $0.01 per interface endpoint per AZ-hour. This rate verification
does not make the monthly totals a quote.

Assumptions:
- Region: `us-east-1`
- Planning month: 730 hours
- Hourly rate: $0.01 per interface endpoint per AZ-hour
- Baseline: `ssm` and `ssmmessages`
- Three-endpoint scenario adds `ec2messages` only for compatibility
  testing
- Data processing, tax, and other service charges excluded

| Configuration | Monthly endpoint-hour estimate |
|---|---:|
| Two endpoints in one AZ | $14.60 |
| Two endpoints in two AZs | $29.20 |
| Three endpoints in one AZ | $21.90 |
| Three endpoints in two AZs | $43.80 |

For a bounded eight-hour session, two endpoints in one AZ have an
estimated endpoint-hour cost of $0.16, assuming both remain active
for exactly eight hours. Data processing and other resources are
additional. Actual billing depends on endpoint uptime and applicable
charges. Confirm pricing again before deployment.

## 4. Trade-offs

- One AZ lowers the learning-session fixed cost but is not an
  implementation of the two-AZ resilience target.
- Two AZs provide an endpoint path in each AZ but incur higher
  hourly charges.
- Interface endpoints do not provide general internet egress.
- S3 gateway endpoints have no endpoint hourly charge.
- Existing security groups and route tables remain unchanged until
  a reviewed implementation plan is approved.

## 5. Validation and cleanup gates

Before deployment:

1. Confirm endpoint service names, Availability Zone support, and
   private-DNS prerequisites using AWS API results.
2. Confirm the EC2 instance profile, role permissions, and SSM Agent
   prerequisites for the selected AMI.
3. Define the endpoint security-group ingress rule and verify the
   required DNS behavior.
4. Confirm the regional price, planned session duration, and spending
   guardrails.
5. Prepare CloudFormation templates and review the change set before
   any approved deployment.
6. Record the exact resources created during the session.

After the approved lab session:

1. Verify Session Manager connectivity and record the test result.
2. Terminate the lab EC2 instance.
3. Delete the temporary interface endpoints.
4. Delete the dedicated endpoint security group only after confirming
   no remaining resources use it.
5. Run read-only inventory checks for remaining endpoints, EC2
   instances, ENIs, and other lab resources.
6. Review applicable billing data later; billing visibility may lag.
7. Preserve shared VPC, IAM, and other baseline resources unless a
   separately approved cleanup plan explicitly includes them.

No deployment or cleanup action is authorized by this checklist.

## 6. Status boundary

This document records a proposal only. It does not establish that
Stage 3 requirements have been implemented or validated.

## 7. Additional read-only evidence

The following checks were completed during network planning. They
describe configuration and service metadata; they do not establish
successful end-to-end Session Manager connectivity.

### 7.1 Subnets and DNS

- App-A: `10.0.11.0/24` in `us-east-1a`.
- App-B: `10.0.12.0/24` in `us-east-1b`.
- Both app subnets have `MapPublicIpOnLaunch` set to false.
- VPC DNS support and DNS hostnames are enabled.
- The app route table has only the local VPC route; no default
  internet route was observed.

### 7.2 SSM endpoint service metadata

Read-only endpoint-service discovery returned the following
Interface endpoint services in `us-east-1`:

- `ssm`
- `ssmmessages`
- `ec2messages`

All three reported availability in `us-east-1a` and `us-east-1b`.
This confirms service availability metadata, not the existence or
configuration of deployed VPC endpoints.

The proposed baseline remains `ssm` and `ssmmessages`.
Include `ec2messages` only if compatibility evidence requires it.

### 7.3 IAM prerequisites

- Instance profile `MedFlow-EC2-SSM-Profile` exists and contains
  `MedFlow-EC2-SSM-Role`.
- The role trust policy allows `ec2.amazonaws.com` to assume it.
- `AmazonSSMManagedInstanceCore` is attached.
- No inline role policies were reported by the inspection.

These findings do not prove that a future EC2 instance will register
successfully with Systems Manager.

### 7.4 Security groups and network ACLs

- `MedFlow-App-SG` permits inbound TCP 80 from `MedFlow-ALB-SG`.
- `MedFlow-App-SG` currently permits all outbound IPv4 traffic.
- No dedicated endpoint security group was found in the VPC inventory.
- The app subnets use the default network ACL, which allows all IPv4
  ingress and egress.
- The data subnets use a custom restrictive network ACL.

No security-group rules, network ACLs, or route tables were changed.

### 7.5 Pricing verification boundary

AWS interface endpoint pricing is based on endpoint usage per
Availability Zone and also includes applicable data-processing
charges. The hourly rate used in Section 3 remains an illustrative
assumption until the exact current `us-east-1` rate is confirmed.

### 7.6 Resource-change boundary

These checks were read-only. No interface endpoints, NAT Gateways,
EC2 instances, routes, security-group rules, or IAM resources were
created or modified as part of this planning sequence.

## SSM Agent AMI evidence boundary

**Status:** AMI metadata verified; exact-image SSM Agent version and runtime connectivity not verified.

### Read-only evidence

- Public parameter: `/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64`
- Parameter version observed: `191`
- AMI ID: `[AMI_ID_REDACTED]`
- AMI name: `al2023-ami-2023.12.20260930.0-kernel-6.18-x86_64`
- Owner ID: `[AMI_OWNER_ID_REDACTED]`
- Creation date: `2026-09-29T19:49:02Z`
- State: `available`
- Architecture: `x86_64`

### Interpretation and limits

The public parameter and EC2 image metadata confirm the selected AMI identity and availability. They do not expose the exact installed `amazon-ssm-agent` package version or prove that the agent is running.

AWS documentation describes `ssmmessages` preference for SSM Agent version `3.3.40.0` and later. This supports the proposed `ssm` plus `ssmmessages` endpoint design, but the exact-image prerequisite remains pending runtime validation.

### Deployment gate

Before treating Session Manager connectivity as validated, an explicitly approved lab must verify the running agent version and managed-node connectivity. Also validate endpoint DNS resolution, endpoint security-group rules, instance IAM permissions, and Session Manager access.

No instance launch, endpoint deployment, or other AWS resource change is authorized by this evidence entry.
