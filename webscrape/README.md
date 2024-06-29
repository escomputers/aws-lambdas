## webscrape
Script to scrape a webpage using a combination of HTML tags and CSS selectors to make the code more tolerant to webpage changes.

In this example, webscraping is used to fetch job listings from a webpage, filter out based on string, if a match is found, send an email. To keep track of already found job listing already found, it uses an S3 file as database for processed jobs.

### Requirements
- Environment variable: `GMAIL_APP_PASSWORD`
- [IAM role for S3 access](iam_policy.json)
- Timeout: 90secs
- Memory size: 256MB
- Tested Runtime: python3.12

### Event example
```json
{
    "gmail_address": "gmail-address@gmail.com",
    "url": "https://kube.careers/remote-kubernetes-jobs",
    "s3_filename": "kubecareers-processed_jobs.json",
    "pattern_to_search": "remote from europe",
    "s3_bucket_name": "s3-bucket-name"
}
```