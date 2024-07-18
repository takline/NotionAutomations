# pipedream add-package boto3
import http.client
import json
import os
import urllib
import boto3
import time
import urlparse


class SecretsManager:
    @staticmethod
    def get_secrets():
        secret_name = os.environ.get("NOTION_GPT_SECRET_NAME", "notionGPT")
        region_name = os.environ.get("AWS_REGION", "us-east-1")

        session = boto3.session.Session()
        client = session.client(service_name="secretsmanager", region_name=region_name)
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        return json.loads(get_secret_value_response["SecretString"])


class NotificationSender:
    @staticmethod
    def send_notification(title, note_json, secrets):
        conn = http.client.HTTPSConnection("api.pushover.net", 443)
        message = note_json["properties"]["Task name"]["title"][0]["plain_text"]
        url = note_json["url"].replace("https://www.notion.so/", "notion://notion.so/")
        payload = {
            "token": secrets["PUSHOVER_APP"],
            "user": secrets["PUSHOVER_USER"],
            "title": title,
            "message": message,
            "url": url,
            "url_title": "Open Notion",
        }
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        conn.request("POST", "/1/messages.json", urlparse.urlencode(payload), headers)
        conn.getresponse()
        return 200


def process_tasks(task_list, message, sleep_time, secrets):
    for task in task_list:
        NotificationSender.send_notification(message, task, secrets)
        time.sleep(sleep_time)


def handler(pd):
    secrets = SecretsManager.get_secrets()

    today = pd.steps["Today_tasks"]["$return_value"]["results"]
    upcoming = pd.steps["Upcoming_tasks"]["$return_value"]["results"]
    late = pd.steps["Late_tasks"]["$return_value"]["results"]

    sleep_time = 5
    total_tasks = len(today) + len(late) + len(upcoming)
    total_available_time = 250.0
    max_sleep_time_per_task = (
        total_available_time / total_tasks if total_tasks else total_available_time
    )

    process_tasks(today, "Task due today", max_sleep_time_per_task, secrets)
    process_tasks(upcoming, "Upcoming tasks due", max_sleep_time_per_task, secrets)
    process_tasks(late, "Late task", max_sleep_time_per_task, secrets)

    return "Complete"
