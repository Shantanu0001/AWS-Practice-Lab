# Stage 1 Route 53 Evidence

Date: 2026-10-05
Project: MedFlow Claims
Stage: 1 — Learning Lab
Region: us-east-1

## Decision

Route 53 public hosted zone deployment is intentionally deferred for the Learning Lab.

## Reason

The lab does not currently have a domain name that the learner owns or is authorized to administer.

A public hosted zone is useful when routing a controlled domain name to AWS resources. Creating a hosted zone without a domain under the learner's control would not provide a meaningful DNS validation exercise and would introduce unnecessary cost.

## Current application access

The Stage 1 application is already validated through the Application Load Balancer's AWS-provided DNS name.

The ALB is:
- Internet-facing
- Active
- Deployed across the two public subnets
- Successfully returning HTTP 200
- Forwarding to the healthy private EC2 target

Therefore, application reachability does not depend on Route 53 for the current Learning Lab.

## Security and cost decision

No Route 53 public hosted zone was created.

This avoids:
- Registering a new domain solely for the lab
- Introducing an unnecessary recurring hosted-zone cost
- Making DNS delegation changes without a controlled domain

This is an intentional Stage 1 deferral, not an implementation failure.

## Future exercise

Route 53 can be added later when a domain is legitimately available for the learner to administer.

The future exercise should include:
1. Create a public hosted zone for the controlled domain.
2. Create an alias record pointing the application hostname to the ALB.
3. Delegate the domain to the Route 53 name servers where required.
4. Validate DNS resolution.
5. Remove the hosted zone after the bounded exercise if it is no longer required.

## Evidence status

Route 53 public DNS: DEFERRED BY DECISION

Reason:
No controlled domain is currently available.

Alternative validated:
ALB AWS DNS name provides working application access for the Stage 1 Learning Lab.
