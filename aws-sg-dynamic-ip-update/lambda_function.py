import boto3
import socket

# AWS clients
ec2 = boto3.client('ec2')

# Security Group and FQDN configuration
security_group_id = 'sg-02d30773db2e41006'
rule_id = 'sgr-09045b11c86016937'
fqdn = 'home.nodbit.com'


def lambda_handler(event, context):
    try:
        # Fetch the public IP address for the FQDN
        ip_address = get_public_ip_from_fqdn(fqdn)

        # Update the security group inbound rule
        update_security_group(security_group_id, rule_id, ip_address)

        return {
            'statusCode': 200,
            'body': f'Security group rule updated with IP: {ip_address}'
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error: {str(e)}'
        }


def get_public_ip_from_fqdn(fqdn):
    try:
        ip_address = socket.gethostbyname(fqdn)
        return ip_address
    except socket.gaierror:
        raise Exception(f'Could not resolve IP address for FQDN: {fqdn}')


def update_security_group(security_group_id, rule_id, ip_address):
    try:
        ec2.modify_security_group_rules(
            GroupId=security_group_id,
            SecurityGroupRules=[
                {
                    'SecurityGroupRuleId': rule_id,
                    'SecurityGroupRule':
                        {
                            'IpProtocol': 'TCP',
                            'FromPort': 8291,
                            'ToPort': 8291,
                            'CidrIpv4': f'{ip_address}/32',
                            'Description': 'Updated via Lambda'
                        }
                }
            ]
        )
    except Exception as e:
        raise Exception(f'Error updating security group rule: {str(e)}')


# ONLY FOR TESTING VIA CLI
# ip_address = get_public_ip_from_fqdn(fqdn)
# update_security_group(security_group_id, rule_id, ip_address)