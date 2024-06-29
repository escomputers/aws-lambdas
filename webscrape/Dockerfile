# Dockerfile for building the deployment .zip package
FROM public.ecr.aws/lambda/python:3.12

# Copy requirements.txt
RUN dnf install zip -y

WORKDIR /home

COPY . .

# Install the specified packages
RUN mkdir -p modules/ && pip install \
  --platform manylinux2014_x86_64 \
  --only-binary=:all: --upgrade \
  -r requirements.txt --target modules/ \
  --implementation cp && \
  cd modules/ && \
  zip -r ../package.zip . \
  && cd .. 

RUN zip package.zip lambda_function.py

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "lambda_function.lambda_handler" ]