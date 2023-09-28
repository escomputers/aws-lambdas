### Description
Update an AWS security group 

### Usage
```bash
mkdir env
python -m venv env
source env/bin/activate
python -m pip install setuptools
python -m pip install -r requirements.txt
rsync -a modules env/lib/python3.X/site-packages/
deactivate
cd env/lib/python3.X/site-packages
zip -r ../../../../my-deployment-package.zip .
cd ../../../../
zip -g my-deployment-package.zip lambda_function.py
```