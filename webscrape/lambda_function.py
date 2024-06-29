"""Script to get notified whenever a job matching a string
is found within kube.careers website"""

import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import boto3
import botocore
import requests
from bs4 import BeautifulSoup

# Constants
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


def send_email(address: str, password: str, subject: str, emailbody=None):
    """Function for sending emails"""
    msg = MIMEMultipart()
    msg["From"] = address  # Send an email to ourselves
    msg["To"] = address
    msg["Subject"] = subject

    if emailbody:
        parsed_body = ""
        # Generate the email body content
        for link, details in emailbody.items():
            parsed_body += f"Title: {details['title']}\n"
            parsed_body += f"Description: {details['description']}\n"
            parsed_body += f"Link: {link}\n\n"

        msg.attach(MIMEText(parsed_body, "plain"))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(address, password)
        server.send_message(msg)
        print("Email sent")


def update_s3_file_content(filecontent: dict, file_name: str, s3_bucket: str):
    """Function for marking a job as processed"""
    # Init AWS Client
    s3_client = boto3.client("s3")

    try:
        s3_client.put_object(
            Body=json.dumps(filecontent), Bucket=s3_bucket, Key=file_name
        )
        print(f"File s3://{s3_bucket}/{file_name} updated successfully")
    except botocore.exceptions.ClientError as e:
        print("Cannot write S3 file")
        raise e


def filter_job_listings(li_elements: list, search_patterns: list) -> dict:
    """Function for getting desired job listings only if there are matched jobs,
    returns a dictionary containing job listing details"""
    results = {}

    for element in li_elements:
        for pattern in search_patterns:
            # Try to find the span with the search pattern using CSS selector
            remote_span = element.select_one(f'span.dotted:-soup-contains("{pattern}")')
            if not remote_span:
                # Fallback to using find_all and checking text content
                spans = element.find_all("span", class_="dotted")
                remote_span = next(
                    (span for span in spans if pattern in span.get_text()), None
                )

            if remote_span:
                # Try to find the title tag using CSS selector
                title_tag = element.select_one("p.mv0.f3.lh-title")
                if not title_tag:
                    # Fallback to using find method
                    title_tag = element.find("p", class_="mv0 f3 lh-title")

                if title_tag:
                    title = title_tag.get_text().strip()
                    link_tag = title_tag.find("a")
                    link = link_tag["href"] if link_tag else "No link found"

                    # Collect all span.dotted elements' text for description
                    description = " ".join(
                        span.get_text() for span in element.select("span.dotted")
                    )
                    if not description:
                        # Fallback to using find_all if select doesn't return anything
                        spans = element.find_all("span", class_="dotted")
                        description = " ".join(span.get_text() for span in spans)

                    # Print the extracted information
                    print()
                    print(f"Title: {title}")
                    print(f"Link: {link}")
                    print(f"Description: {description.strip()}")
                    print("-----")
                    print()

                    results[link] = {"title": title, "description": description.strip()}

    return results


def fetch_webpage_list_elements(webpage_url: str) -> object:
    """Function for getting webpage list elements containing job listings"""
    response = requests.get(webpage_url, timeout=20)
    if response.status_code == 200:
        # Select only HTML list elements
        return BeautifulSoup(response.text, "html.parser").select('li[class=""]')

    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
    return []


def get_s3_file_content(file_name: str, s3_bucket: str) -> dict:
    """Function for getting the database file from the S3 private bucket
    storing already processed jobs"""

    # Init AWS Client
    s3_client = boto3.client("s3")

    file_content = {}
    try:
        response = s3_client.get_object(
            Bucket=s3_bucket,
            Key=file_name,
        )
        file_content.update(json.loads(response["Body"].read().decode("utf-8")))
        return file_content
    except botocore.exceptions.ClientError:
        return {}


def lambda_handler(event: dict, context: dict) -> json:
    """Main AWS Lambda handler function"""
    # Event variables
    url = event["url"]
    filename = event["s3_filename"]
    email_username = event["gmail_address"]
    email_password = os.getenv("GMAIL_APP_PASSWORD")
    patterns = event["patterns_to_search"]
    s3_bucket_name = event["s3_bucket_name"]

    # Retrieve S3 database file content
    print("Checking S3 database file content...")
    file_content = get_s3_file_content(filename, s3_bucket_name)
    print("Fetched S3 database file content")

    # Retrieve webpage list elements
    print(f"Retrieving webpage content: {url}...")
    webpage_list_elements = fetch_webpage_list_elements(url)
    print("Retrieved webpage content")

    # Error case when webpage content cannot be retrieved
    if len(webpage_list_elements) == 0:
        print(f"Cannot retrieve {url} content")
        send_email(email_username, email_password, f"Error fetching content on {url}")
        return json.dumps(
            {"statusCode": 500, "body": f"Error fetching content on {url}"}
        )

    # Check if any job listing inside all li elements matches the search criteria
    print("Checking job listings for matches...")
    matched_jobs = filter_job_listings(webpage_list_elements, patterns)

    if matched_jobs:
        print("Found job listings matching search criteria")

        # Init dictionary storing new jobs only for email notification
        email_body = {}
        # Initialize the flag to track if any new key is found
        new_key_found = False

        print("Checking if results have been already processed...")
        for key, value in matched_jobs.items():
            # Update S3 database file (dictionary) with new matches only
            if key not in file_content.keys():
                # Set the flag to True if a new key is found
                new_key_found = True
                file_content[key] = value  # Update dictionary for S3 file
                email_body[key] = value  # Update dictionary for email body
        if not new_key_found:
            # Results are found but they were all already processed
            print("Results are already in database file, nothing to do")
            return json.dumps(
                {
                    "statusCode": 304,
                    "body": "Results are already in database file, nothing to do",
                }
            )

        # Send email
        if email_body:
            print("Sending email...")

            send_email(
                email_username,
                email_password,
                "New job listings from kube.careers!",
                email_body,
            )

            # Update S3 database file
            print(f"Updating database file s3://{s3_bucket_name}/{filename}...")
            update_s3_file_content(file_content, filename, s3_bucket_name)

            return json.dumps(
                {
                    "statusCode": 200,
                    "body": "Email with new job listings sent",
                }
            )

    # No matches found case
    print("No job listings match search criteria")
    return json.dumps(
        {"statusCode": 304, "body": "No job listings match search criteria"}
    )


evento = {
    "gmail_address": "emilianos13@gmail.com",
    "url": "https://kube.careers/remote-kubernetes-jobs",
    "s3_filename": "kubecareers-processed_jobs.json",
    "patterns_to_search": ["remote from Europe", "remote from Italy"],
    "s3_bucket_name": "personal-864430642600",
}
contesto = {}
lambda_handler(evento, contesto)
