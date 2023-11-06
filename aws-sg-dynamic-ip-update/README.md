### Description
Fetch public IP address from a FQDN and the update an AWS security group inbound rule for "source" field.

### Setup
Edit these keys and values in lambda_function.py according to desired network ports.
```python
  'FromPort': 8291,
  'ToPort': 8291,
```

### Test event
```json
{
  "security_group_id": "sg-02d30773db2e41006",
  "rule_id": "sgr-09045b11c86016937",
  "fqdn": "home.nodbit.com"
}
```

### Cron expression for EventBridge trigger source
```
### every 15 minutes
rate(15 minutes)
```