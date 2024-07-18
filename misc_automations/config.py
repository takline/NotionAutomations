import http.client
import json
import os
import urllib

import boto3
from google.cloud import storage
from google.oauth2 import service_account
from notion_client import Client


def create_notion_page(summary_content, notion_client, ios=False):
    """Create a new page in Notion based on the summary content."""
    response = notion_client.pages.create(
        parent={"database_id": config.SECRETS["MEDIA_SAVES_DB"]},
        properties={
            "Name": {"title": [{"text": {"content": summary_content["TITLE"]}}]},
            "Key points": {
                "rich_text": [{"text": {"content": summary_content["KEYPOINTS"]}}]
            },
            "Summary": {
                "rich_text": [{"text": {"content": summary_content["SUMMARY"]}}]
            },
            "Tags": {
                "multi_select": [{"name": tag} for tag in summary_content["TAGS"]]
            },
        },
    )
    if ios:
        notion_url = response["url"].replace(
            "https://www.notion.so/", "notion://notion.so/"
        )
    else:
        notion_url = response["url"]
    return notion_url


def get_secrets():
    secret_name = "notionGPT"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session(os.environ["AWSKEY"], os.environ["AWSSECRET"])
    client = session.client(service_name="secretsmanager", region_name=region_name)

    get_secret_value_response = client.get_secret_value(SecretId=secret_name)

    secret = get_secret_value_response["SecretString"]

    return json.loads(secret)


def send_notification(message):
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request(
        "POST",
        "/1/messages.json",
        urllib.parse.urlencode(
            {
                "token": SECRETS["PUSHOVER_APP"],
                "user": SECRETS["PUSHOVER_USER"],
                "message": message,
            }
        ),
        {"Content-type": "application/x-www-form-urlencoded"},
    )
    conn.getresponse()
    return 200


SECRETS = get_secrets()
GITHUB_REPO_URL = "git@github.com:takline/automation.git"
S3_CLIENT = boto3.client(
    "s3",
    aws_access_key_id=SECRETS["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=SECRETS["AWS_SECRET"],
)
S3_RESOURCE = boto3.resource(
    "s3",
    "us-east-1",
    aws_access_key_id=SECRETS["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=SECRETS["AWS_SECRET"],
)
NOTION_CLIENT = Client(auth=SECRETS["NOTION"])
GCS_CREDENTIALS = service_account.Credentials.from_service_account_file(
    "google_auth.json"
)
GCS_CLIENT = storage.Client(credentials=GCS_CREDENTIALS)
