###Trim_mp4_and_send_to_GCP###
# This script is responsible for downloading a video from a Notion database, potentially compressing it, and then uploading it to Google Cloud Storage.
# pipedream add-package moviepy
# pipedream add-package google-cloud-aiplatform
import os
import requests
from google.oauth2 import service_account
from google.cloud import storage
from moviepy.editor import VideoFileClip


def save_creds():
    """A hack within pipedream env to save Google Cloud credentials to a temporary file."""
    auth = {
        "type": "service_account",
        "project_id": os.getenv("GOOGLE_PROJECT_ID"),
        "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
        "private_key": os.getenv("GOOGLE_PRIVATE_KEY").replace("\\n", "\n"),
        "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.getenv("CLIENT_CERT_URL"),
        "universe_domain": "googleapis.com",
    }
    with open("/tmp/google_auth.json", "w") as outfile:
        json.dump(auth, outfile)


def upload_blob(storage_client, bucket_name, source_file_name, destination_blob_name):
    """
    Uploads a file to a specified Google Cloud Storage bucket.

    :param storage_client: Initialized Google Cloud Storage client.
    :param bucket_name: Name of the Google Cloud Storage bucket.
    :param source_file_name: Path to the file to be uploaded.
    :param destination_blob_name: Name to be assigned to the file in the bucket.
    """
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(f"File {source_file_name} uploaded to {destination_blob_name}.")


def download_video(url, filename):
    """
    Downloads a video from a given URL and saves it to a local file.

    :param url: URL of the video to be downloaded.
    :param filename: Local path where the video will be saved.
    """
    response = requests.get(url, stream=True)
    with open(filename, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)


def compress_video(input_filename, target_size_MB):
    """
    Compresses the video to a specified size.

    :param input_filename: Path to the input video file.
    :param target_size_MB: Target size of the video in Megabytes.
    """
    clip = VideoFileClip(input_filename)

    # Calculate the target bitrate based on the target size (in bits)
    target_size_bits = target_size_MB * 8 * 1024 * 1024
    duration = clip.duration
    target_bitrate = target_size_bits / duration

    # Compress the video
    clip.write_videofile(input_filename, bitrate=target_bitrate)


def handler(pd: "pipedream"):
    """
    Main handler function for processing video files.

    :param pd: Pipedream context object containing information about the trigger event.
    :returns: Path to the processed video file.
    """
    mp4_file = "/tmp/video.mp4"
    max_size_MB = 9
    notion_video_url = pd.steps["retrieve_block"]["$return_value"]["children"][0][
        "video"
    ]["file"]["url"]

    download_video(notion_video_url, mp4_file)
    original_size_MB = os.path.getsize(mp4_file) / (1024 * 1024)

    if original_size_MB <= max_size_MB:
        print("File size is already under 9MB, no need to compress.")
    else:
        compress_video(mp4_file, max_size_MB)

    save_creds()
    credentials = service_account.Credentials.from_service_account_file(
        "/tmp/google_auth.json"
    )

    storage_client = storage.Client(credentials=credentials)
    upload_blob(
        storage_client,
        bucket_name=os.getenv("GOOGLE_BLOB"),
        source_file_name=mp4_file,
        destination_blob_name="video.mp4",
    )

    # Return data for use in future steps
    return mp4_file


###Send_to_Gemini###
# This code interfaces with Google's Gemini model to generate a summary of the video, which is then formatted.
# pipedream add-package google-cloud-aiplatform
import json
import os
import requests
import vertexai
from vertexai.preview.generative_models import GenerativeModel
from vertexai.preview import generative_models
from google.oauth2 import service_account
import re


def save_creds():
    auth = {
        "type": "service_account",
        "project_id": os.getenv("GOOGLE_PROJECT_ID"),
        "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
        "private_key": os.getenv("GOOGLE_PRIVATE_KEY").replace("\\n", "\n"),
        "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.getenv("CLIENT_CERT_URL"),
        "universe_domain": "googleapis.com",
    }
    with open("/tmp/google_auth.json", "w") as outfile:
        json.dump(auth, outfile)


def get_video_summary():
    """
    Generates a summary for a video using the Gemini model.

    :returns: A string containing the HTML-formatted summary of the video.
    """
    save_creds()
    credentials = service_account.Credentials.from_service_account_file(
        "/tmp/google_auth.json"
    )

    vertexai.init(
        credentials=credentials,
        project=os.getenv("GOOGLE_PROJECT_ID"),
        location=os.getenv("GOOGLE_LOCATION"),
    )
    gemini_pro_vision_model = GenerativeModel("gemini-pro-vision")

    response = gemini_pro_vision_model.generate_content(
        [
            """Imagine yourself as a visionary leader in the field of technology and innovation, akin to well-known figures like Sam Altman. Your expertise is in identifying and interpreting emerging trends in technology, startups, and global developments. You have recently viewed a short video that you find particularly insightful in terms of its implications for the future. Your task is to create a comprehensive summary of this video that includes:
- a creative title that captures the essence of the video
- 3-5 bullet points highlighting the key takeaways
- a 3-5 sentence summary offering a deeper analysis of how these points relate to broader trends and their potential impact on startups and the world at large. 
- 0-3 one-word tags that you choose to label the video as (so that you can categorize and analyze at a later time)

Please format your response using HTML tags as follows:

<TITLE> [Your creative title here] </TITLE>
<KEYPOINTS>
- [Key point 1]
- [Key point 2]
- [Key point 3]
</KEYPOINTS>
<SUMMARY> [Your analytical summary here, encompassing the key insights and their wider implications] </SUMMARY>
<TAGS> [comma seperated 1-word tags that you choose to label the video as] </TAGS>""",
            generative_models.Part.from_uri(
                "gs://notion3000/video.mp4", mime_type="video/mp4"
            ),
        ],
        stream=True,
    )

    final = ""
    for chunk in response:
        final += chunk.text
    return final


def parse_html_tags(input_string):
    """
    Extracts content from HTML tags in a string.

    :param input_string: String containing HTML-tagged content.
    :returns: A dictionary with parsed content categorized by HTML tags.
    """
    # Define a dictionary to hold the parsed content
    parsed_content = {"TITLE": "", "KEYPOINTS": "", "SUMMARY": "", "TAGS": []}

    # Define regular expression patterns for each tag
    title_pattern = r"<TITLE>(.*?)</TITLE>"
    keypoints_pattern = r"<KEYPOINTS>(.*?)</KEYPOINTS>"
    summary_pattern = r"<SUMMARY>(.*?)</SUMMARY>"
    tags_pattern = r"<TAGS>(.*?)</TAGS>"

    # Extract content for each tag
    title_match = re.search(title_pattern, input_string, re.DOTALL)
    if title_match:
        parsed_content["TITLE"] = title_match.group(1).strip()

    keypoints_match = re.search(keypoints_pattern, input_string, re.DOTALL)
    if keypoints_match:
        parsed_content["KEYPOINTS"] = keypoints_match.group(1).strip()

    summary_match = re.search(summary_pattern, input_string, re.DOTALL)
    if summary_match:
        parsed_content["SUMMARY"] = summary_match.group(1).strip()

    tags_match = re.search(tags_pattern, input_string, re.DOTALL)
    if tags_match:
        # Split the keypoints into a list
        tags = tags_match.group(1).strip().split(",")
        tags = [x.strip() for x in tags]
        # Clean up each keypoint
        parsed_content["TAGS"] = tags

    return parsed_content


def handler(pd: "pipedream"):
    """
    Main handler function for summarizing video content.

    :param pd: Pipedream context object containing information about the trigger event.
    :returns: A dictionary containing the parsed summary of the video.
    """
    summary = get_video_summary()
    return parse_html_tags(summary)
