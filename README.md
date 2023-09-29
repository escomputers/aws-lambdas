### Deploy Lambda function using a .zip archive
```bash
mkdir -p modules
python -m pip install -r requirements.txt --target modules/
cd modules && zip -r ../package.zip .
cd .. && zip package.zip lambda_function.py
```