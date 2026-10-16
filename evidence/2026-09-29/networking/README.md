# Stage 1 VPC Evidence

Date: 29 September 2026

## VPC

- Name: `MedFlow-Stage1-VPC`
- Region: `us-east-1`
- CIDR: `10.0.0.0/16`
- Default VPC: `false`

## DNS Configuration

- DNS support: enabled
- DNS hostnames: enabled

## Verification

The VPC was created using the AWS CLI with the
`local-profile` temporary AWS CLI login profile.

Verification performed with:

- `aws ec2 describe-vpcs`
- `aws ec2 describe-vpc-attribute --attribute enableDnsSupport`
- `aws ec2 describe-vpc-attribute --attribute enableDnsHostnames`

## Cost Boundary

No NAT Gateway or other intentionally cost-bearing network
resource was created at this checkpoint.

## Result

VPC creation and DNS configuration verified successfully.

## Next Step

Create the six Stage 1 subnets defined in:

`docs/04-network-design-stage1.md`