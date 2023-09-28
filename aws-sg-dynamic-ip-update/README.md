### Description
Fetch public IP address from a FQDN and the update an AWS security group inbound rule for "source" field.

### Usage
```bash
mkdir -p env && python -m venv env
source env/bin/activate
python -m pip install -r requirements.txt
rsync -a modules env/lib/python3.X/site-packages/
deactivate
cd env/lib/python3.X/site-packages
zip -r ../../../../my-deployment-package.zip .
cd ../../../../
zip -g my-deployment-package.zip lambda_function.py
```