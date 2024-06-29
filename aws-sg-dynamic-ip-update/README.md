## aws-sg-dynamic-ip-update
Fetch public IP address from a FQDN and the update an AWS security group inbound rule "source" field.

### Requirements
- IAM role for EC2 SG group access
- Timeout: 30secs
- Memory size: 256MB
- Tested Runtime: python3.12

### Setup
Edit these keys and values in lambda_function.py according to desired network ports.
```python
  'FromPort': 8291,
  'ToPort': 8291,
```

### Event example
```json
{
  "security_group_id": "sg-02d30773db2e41006",
  "rule_id": "sgr-09045b11c86016937",
  "fqdn": "home.nodbit.com"
}
```

### Cron expression for EventBridge trigger source
```bash
### every 15 minutes
rate(15 minutes)
```