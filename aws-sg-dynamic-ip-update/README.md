### Description
Fetch public IP address from a FQDN and the update an AWS security group inbound rule for "source" field.

### Usage
```bash
mkdir -p env && python -m venv env
source env/bin/activate
python -m pip install -r requirements.txt
```

### Test event
```json
{
  "security_group_id": "sg-02d30773db2e41006",
  "rule_id": "sgr-09045b11c86016937",
  "fqdn": "home.nodbit.com"
}
```