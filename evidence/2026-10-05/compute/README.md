# MedFlow Stage 1 Compute Evidence

## Date

2026-10-05

## EC2 instance

- Name: `MedFlow-App-A-01`
- Instance ID: `[EC2_INSTANCE_ID_REDACTED]`
- Instance type: `t3.micro`
- Availability Zone: `us-east-1a`
- Subnet: `[APP_SUBNET_A_ID_REDACTED]`
- Private IP: `10.0.11.176`
- Public IPv4: none
- Security Group: `MedFlow-App-SG`
- IAM instance profile: `MedFlow-EC2-SSM-Profile`
- IMDSv2: required
- CPU credit mode: standard

## Root EBS volume

- Volume ID: `[AWS_RESOURCE_ID_REDACTED]`
- Device: `/dev/xvda`
- Size: `8 GiB`
- Type: `gp3`
- Encrypted: `true`
- State: `in-use`

## Systems Manager

- SSM Agent version: `3.3.5226.0`
- Ping status: `Online`
- Platform: `Amazon Linux`

## Security validation

- No public IPv4 address assigned.
- No SSH key pair was configured at launch.
- No inbound SSH/22 rule exists for the application security group.
- Instance is managed through AWS Systems Manager rather than inbound SSH.

## Network dependency

The private App subnet reaches outbound services through the temporary Stage 1 NAT Gateway:

- NAT Gateway: `[NAT_GATEWAY_ID_REDACTED]`
- App route table: `[APP_ROUTE_TABLE_ID_REDACTED]`
- Default route: `0.0.0.0/0 -> NAT Gateway`

The Data route table remains isolated from the NAT Gateway and Internet Gateway.

## Status

Stage 1 EC2 and SSM foundation verified.

Application configuration, ALB, target group, and health-check validation remain incomplete.

## Interactive SSM session

An interactive AWS Systems Manager Session Manager session was successfully established to `[EC2_INSTANCE_ID_REDACTED]`.

Verified inside the instance:

- `whoami` returned `ssm-user`.
- `hostname` returned the private EC2 hostname.
- `/etc/os-release` confirmed Amazon Linux 2023.
- Session was exited normally with `exit`.

This confirms operational management through Systems Manager without inbound SSH.

## Application service

[DECISION — 2026-10-05] Nginx is used as the minimal Stage 1 HTTP application implementation for validating the EC2 application tier and ALB path.

- Package: `nginx`
- Version: `1.30.5`
- Service: `nginx`
- Service state: `active (running)`
- Service enabled at boot: `true`
- Listener: TCP/80 on IPv4 and IPv6
- Local HTTP test: `curl -I http://127.0.0.1`
- HTTP result: `200 OK`

This is a Stage 1 lab implementation choice. It does not represent the final MedFlow application technology.

## Compute status update

The EC2-hosted HTTP application is operational.

Target group, ALB, external HTTP validation, and ALB health-check validation were not yet complete at the time of the earlier checkpoint; they are now validated below.

## ALB and end-to-end HTTP validation

The Stage 1 Application Load Balancer was verified from the external Windows workstation.

- ALB DNS: `MedFlow-ALB-599910236.us-east-1.elb.amazonaws.com`
- Listener: HTTP/80
- Target group: `MedFlow-App-TG`
- Target: `[EC2_INSTANCE_ID_REDACTED]`
- Target health: `healthy`
- External HEAD request: `HTTP/1.1 200 OK`
- External GET request: `HTTP 200 OK`
- Response server: `nginx/1.30.5`

This validates the end-to-end path from the external client through the Application Load Balancer to the private EC2 application instance.

The returned page is the default Nginx page used for the Stage 1 lab application validation. It is not the final MedFlow application.

## Compute status update

EC2, SSM, Nginx, target group, ALB, listener, target health, and external HTTP validation are complete for the Stage 1 lab.

Auto Scaling and production-grade application behavior remain part of later stages.

## Final Compute security validation

The final Stage 1 security-boundary checks passed.

- `MedFlow-ALB-SG` allows inbound TCP/80 from `0.0.0.0/0`.
- `MedFlow-App-SG` allows inbound TCP/80 only from `MedFlow-ALB-SG`.
- No inbound TCP/22 rule exists in `MedFlow-App-SG`.
- EC2 `[EC2_INSTANCE_ID_REDACTED]` has no public IPv4 address.
- The application instance remains in the private App subnet.
- The previously verified Data route table remains isolated from the Internet Gateway and NAT Gateway.

## Stage 1 Compute completion

Stage 1 Compute is complete for the Learning Lab:

EC2, SSM, Nginx, target group, Application Load Balancer, listener, target health, external HTTP validation, and the final network/security boundary checks have been verified.

Auto Scaling and later production-grade compute improvements remain part of subsequent stages.
