### EC2 user-data script 
#### Right way
```
resource "aws_instance" "app_server" {
    ami           = var.ami_id
    instance_type = var.instance_type
    key_name = var.ssh_api_key
    root_block_device {
        volume_size = 100
        volume_type = "gp3"
    }
    user_data ="${file("setup.sh")}"
    tags = {
        Name = "ShiftLeftService"
    }
}
```
OR
```
resource "aws_instance" "app_server" {
    ami           = var.ami_id
    instance_type = var.instance_type
    key_name = var.ssh_api_key
    root_block_device {
        volume_size = 100
        volume_type = "gp3"
    }
    user_data = <<EOF
#!/bin/bash
/usr/bin/touch /tmp/somefile
EOF
    tags = {
        Name = "ShiftLeftService"
    }
}
```
#### Troubleshoot
Look in /var/log/cloud-init.log
The below entry suggests it executed the user data script
```
2025-01-09 19:39:46,729 - __init__.py[DEBUG]: {'MIME-Version': '1.0', 'Content-Type': 'text/x-shellscript', 'Content-Disposition': 'attachment; filename="part-001"'}
2025-01-09 19:39:46,729 - __init__.py[DEBUG]: Calling handler ShellScriptPartHandler: [['text/x-shellscript']] (text/x-shellscript, part-001, 2) with frequency once-per-instance
2025-01-09 19:39:46,729 - util.py[DEBUG]: Writing to /var/lib/cloud/instance/scripts/part-001 - wb: [700] 40 bytes
2025-01-09 19:39:46,730 - util.py[DEBUG]: Restoring selinux mode for /var/lib/cloud/instances/i-01fdd0878ae17e17b/scripts/part-001 (recursive=False)
2025-01-09 19:39:46,730 - util.py[DEBUG]: Restoring selinux mode for /var/lib/cloud/instances/i-01fdd0878ae17e17b/scripts/part-001 (recursive=False)
```

Check this service as well
FAILURE
```
[ec2-user@ip-172-31-3-125 log]$ systemctl status cloud-final.service
× cloud-final.service - Execute cloud user/final scripts
     Loaded: loaded (/usr/lib/systemd/system/cloud-final.service; enabled; preset: disabled)
     Active: failed (Result: exit-code) since Thu 2025-01-09 19:45:33 UTC; 4min 44s ago
    Process: 2260 ExecStart=/usr/bin/cloud-init modules --mode=final (code=exited, status=1/FAILURE)
   Main PID: 2260 (code=exited, status=1/FAILURE)
        CPU: 404ms

Jan 09 19:45:32 ip-172-31-3-125.us-west-2.compute.internal cloud-init[2272]: 256 SHA256:l5EWohsEEp1SYKt6u6P7hNpAVPudI0LBwiM272xagDw root@ip-172-31-3-125.us-west-2.compute.internal (ECDSA)
Jan 09 19:45:32 ip-172-31-3-125.us-west-2.compute.internal cloud-init[2274]: 256 SHA256:5njpsCsctiIP6N0Yos/9DDgv3Lz7QudxjeggYGY3NKI root@ip-172-31-3-125.us-west-2.compute.internal (ED25519)
Jan 09 19:45:32 ip-172-31-3-125.us-west-2.compute.internal cloud-init[2275]: -----END SSH HOST KEY FINGERPRINTS-----
Jan 09 19:45:32 ip-172-31-3-125.us-west-2.compute.internal cloud-init[2276]: #############################################################
Jan 09 19:45:33 ip-172-31-3-125.us-west-2.compute.internal cloud-init[2266]: Cloud-init v. 22.2.2 finished at Thu, 09 Jan 2025 19:45:33 +0000. Datasource DataSourceEc2.  Up 11.79 seconds
Jan 09 19:45:33 ip-172-31-3-125.us-west-2.compute.internal systemd[1]: cloud-final.service: Main process exited, code=exited, status=1/FAILURE
Jan 09 19:45:33 ip-172-31-3-125.us-west-2.compute.internal systemd[1]: cloud-final.service: Failed with result 'exit-code'.
Jan 09 19:45:33 ip-172-31-3-125.us-west-2.compute.internal systemd[1]: cloud-final.service: Unit process 2266 (tee) remains running after unit stopped.
Jan 09 19:45:33 ip-172-31-3-125.us-west-2.compute.internal systemd[1]: cloud-final.service: Unit process 2279 (cloud-init) remains running after unit stopped.
Jan 09 19:45:33 ip-172-31-3-125.us-west-2.compute.internal systemd[1]: Failed to start cloud-final.service - Execute cloud user/final scripts.
```
SUCCESS
```
[ec2-user@ip-172-31-16-158 tmp]$ systemctl status cloud-final.service
● cloud-final.service - Execute cloud user/final scripts
     Loaded: loaded (/usr/lib/systemd/system/cloud-final.service; enabled; preset: disabled)
     Active: active (exited) since Thu 2025-01-09 19:58:18 UTC; 1min 52s ago
    Process: 2232 ExecStart=/usr/bin/cloud-init modules --mode=final (code=exited, status=0/SUCCESS)
   Main PID: 2232 (code=exited, status=0/SUCCESS)
      Tasks: 0
     Memory: 332.0K
        CPU: 402ms
     CGroup: /system.slice/cloud-final.service

Jan 09 19:58:17 ip-172-31-16-158.us-west-2.compute.internal systemd[1]: Starting cloud-final.service - Execute cloud user/final scripts...
Jan 09 19:58:18 ip-172-31-16-158.us-west-2.compute.internal cloud-init[2240]: Cloud-init v. 22.2.2 running 'modules:final' at Thu, 09 Jan 2025 19:58:18 +0000. Up 12.99 seconds.
Jan 09 19:58:18 ip-172-31-16-158.us-west-2.compute.internal cloud-init[2244]: #############################################################
Jan 09 19:58:18 ip-172-31-16-158.us-west-2.compute.internal cloud-init[2245]: -----BEGIN SSH HOST KEY FINGERPRINTS-----
Jan 09 19:58:18 ip-172-31-16-158.us-west-2.compute.internal cloud-init[2247]: 256 SHA256:3VFChVv93Oq/z5Z7fIzXnp1XPu2sZ5t3dhOewvNFjRs root@ip-172-31-16-158.us-west-2.compute.internal (ECDSA)
Jan 09 19:58:18 ip-172-31-16-158.us-west-2.compute.internal cloud-init[2249]: 256 SHA256:CzxZMeSptv4lLe+GueVNhOapsKGydb8ByBPMLjb1QXg root@ip-172-31-16-158.us-west-2.compute.internal (ED25519)
Jan 09 19:58:18 ip-172-31-16-158.us-west-2.compute.internal cloud-init[2250]: -----END SSH HOST KEY FINGERPRINTS-----
Jan 09 19:58:18 ip-172-31-16-158.us-west-2.compute.internal cloud-init[2251]: #############################################################
Jan 09 19:58:18 ip-172-31-16-158.us-west-2.compute.internal cloud-init[2240]: Cloud-init v. 22.2.2 finished at Thu, 09 Jan 2025 19:58:18 +0000. Datasource DataSourceEc2.  Up 13.35 seconds
Jan 09 19:58:18 ip-172-31-16-158.us-west-2.compute.internal systemd[1]: Finished cloud-final.service - Execute cloud user/final scripts.
```
### Display Account ID
```
[ssahu@mac ~/.aws ]# aws sts get-caller-identity
{
    "UserId": "XXXXXXXXXXXXXXXXXXXXXXXXXX:srsahu@confluent.io",
    "Account": "999999999999",
    "Arn": "arn:aws:sts::999999999999:assumed-role/AWSReservedSSO_nonprod-administrator_6bbd747b1460f5f4/srsahu@confluent.io"
}
```

### Create Access keys for a user
Make sure the ~/.aws/credentials has the right values
```
[ssahu@mac ~/.aws ]# aws iam create-access-key --user-name srinivassahu
{
    "AccessKey": {
        "UserName": "srinivassahu",
        "AccessKeyId": "xxxxxxxxxxxx",
        "Status": "Active",
        "SecretAccessKey": "xxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "CreateDate": "2025-01-07T22:24:37Z"
    }
}
```
### Create Session Token for a user 
NOte: access key & Secret Key of the user required.
```
[ssahu@mac ~/.aws ]# export AWS_ACCESS_KEY_ID="AKIAXXXXXXXXXXXXX"
[ssahu@mac ~/.aws ]# export AWS_SECRET_ACCESS_KEY="XXXXXXXXXXXXXXXXXXXXXXXXXXX"
[ssahu@mac ~/.aws ]# aws sts get-session-token --duration-seconds 129600
{
    "Credentials": {
        "AccessKeyId": "ASIAXXXXXXXXXXXXXXX",
        "SecretAccessKey": "g5sRZxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "SessionToken": "FwoGxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "Expiration": "2025-01-10T05:07:22Z"
    }
}
```
### Display Availablity Zones
Note: Zone-Name to Zone-ID mapping may differ across aws accounts
```
[ssahu@mac ~/terraform ]# aws ec2 describe-availability-zones --query 'AvailabilityZones[*].[ZoneName, ZoneId]' --region us-east-1 --output text
us-east-1a	use1-az4
us-east-1b	use1-az6
us-east-1c	use1-az1
us-east-1d	use1-az2
us-east-1e	use1-az3
us-east-1f	use1-az5
```
### Split /24 cidr block to 3 /27 cidr blocks
```
[ssahu@mac ~terraform ]# terraform console
> cidrsubnets("10.179.8.0/24", 3, 3, 3)
tolist([
  "10.179.8.0/27",
  "10.179.8.32/27",
  "10.179.8.64/27",
])
```
### List s3 buckets
```
> env | grep AWS
AWS_ACCESS_KEY_ID=xxxxxxxxx
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxx
AWS_SESSION_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

[ssahu@mac ~ ]# aws s3 ls
2024-08-02 01:30:47 253791803581-logs
2024-04-22 14:29:14 253791803581-tfstate
2024-08-06 23:20:11 blt-recipes
2024-09-06 21:50:29 cosmetic-validation-content
2024-05-22 00:20:13 datarights-svc-gamedev
2024-10-10 20:53:54 eos-backend-confluent-connector
2024-04-01 19:58:17 eos-backend-customer-events-gamedev
2022-05-16 16:47:29 eos-backend-customer-events-gamedev-recovery
2024-04-01 19:59:12 eos-backend-customer-events-gamedev-temp
2024-05-22 00:12:06 eos-backend-dynamicconfig-nonlive
2021-10-19 02:01:48 eos-backend-tf-state
2023-06-28 15:06:39 sdk-releases-gamedev
```

### InternetGateway Vs NATGateway

#### NAT Gateway
- NAT Gateway (NGW) is a managed Network Address Translation (NAT) service.
- NAT Gateway does something similar to Internet Gateway (IGW), but it only works one way: Instances in a private subnet can connect to services outside your VPC but external services cannot initiate a connection with those instances.
- NAT gateways are supported for IPv4 or IPv6 traffic.
- NAT gateway supports the following protocols: TCP, UDP, and ICMP.
- Each NAT gateway is created in a specific Availability Zone and implemented with redundancy in that zone.
- If you have resources in multiple Availability Zones and they share one NAT gateway, and if the NAT gateway’s Availability Zone is down, resources in the other Availability Zones lose internet access.
- To create an Availability Zone-independent architecture, create a NAT gateway in each Availability Zone.
- You can associate exactly one Elastic IP address with a public NAT gateway.
- You are charged for each hour that your NAT gateway is available and each Gigabyte of data that it processes.

#### Internet Gateway
- Internet Gateway (IGW) is a horizontally scaled, redundant, and highly available VPC component that allows communication between your VPC and the internet.
- Internet Gateway enables resources (like EC2 instances) in public subnets to connect to the internet. Similarly, resources on the internet can initiate a connection to resources in your subnet using the public.
- If a VPC does not have an Internet Gateway, then the resources in the VPC cannot be accessed from the Internet (unless the traffic flows via a Corporate Network and VPN/Direct Connect).
- Internet Gateway supports IPv4 and IPv6 traffic.
- Internet Gateway does not cause availability risks or bandwidth constraints on your network traffic.
- In order to make subnet public, add a route to your subnet’s route table that directs internet-bound traffic to the internet gateway.
- You can associate exactly one Internet Gateway with a VPC.
- Internet Gateway is not Availability Zone specific.
- There’s no additional charge for having an internet gateway in your account.

