# pipedream add-package ffprobe
# pipedream add-package ffmpeg-python
# pipedream add-package google-cloud-aiplatform
# pipedream add-package dropbox
import os
import re
from datetime import datetime
import time
import ffmpeg
from google.cloud import storage
from google.oauth2 import service_account
import json

# pipedream add-package google-cloud-aiplatform
import json
import os
import requests
import vertexai
from vertexai.preview.generative_models import GenerativeModel
from vertexai.preview import generative_models
from google.oauth2 import service_account
import re


def compress_video(
    video_full_path, size_upper_bound, two_pass=True, filename_suffix="cps_"
):
    """
    Compress video file to max-supported size.
    :param video_full_path: the video you want to compress.
    :param size_upper_bound: Max video size in KB.
    :param two_pass: Set to True to enable two-pass calculation.
    :param filename_suffix: Add a suffix for new video.
    :return: out_put_name or error
    """
    output_file_name = video_full_path

    # Adjust them to meet your minimum requirements (in bps), or maybe this function will refuse your video!
    total_bitrate_lower_bound = 11000
    min_audio_bitrate = 32000
    max_audio_bitrate = 256000
    min_video_bitrate = 100000
    print(
        "%s Compressing video: %s",
        datetime.fromtimestamp(time.time()).strftime("%Y%m%d%H%M%S"),
        video_full_path,
    )

    try:
        # Bitrate reference: https://en.wikipedia.org/wiki/Bit_rate#Encoding_bit_rate
        probe = ffmpeg.probe(video_full_path)
        # Video duration, in s.
        duration = float(probe["format"]["duration"])
        # Audio bitrate, in bps.
        audio_bitrate = float(
            next((s for s in probe["streams"] if s["codec_type"] == "audio"), None)[
                "bit_rate"
            ]
        )
        # Target total bitrate, in bps.
        target_total_bitrate = (size_upper_bound * 1024 * 8) / (1.073741824 * duration)
        if target_total_bitrate < total_bitrate_lower_bound:
            print(
                "%s Bitrate is extremely low! Stop compress!",
                datetime.fromtimestamp(time.time()).strftime("%Y%m%d%H%M%S"),
            )
            return False

        # Best min size, in kB.
        best_min_size = (
            (min_audio_bitrate + min_video_bitrate)
            * (1.073741824 * duration)
            / (8 * 1024)
        )
        if size_upper_bound < best_min_size:
            print(
                "%s Quality not good! Recommended minimum size: %s KB.",
                datetime.fromtimestamp(time.time()).strftime("%Y%m%d%H%M%S"),
                "{:,}".format(int(best_min_size)),
            )
            # return False

        # target audio bitrate, in bps
        if 10 * audio_bitrate > target_total_bitrate:
            audio_bitrate = target_total_bitrate / 10
            if audio_bitrate < min_audio_bitrate < target_total_bitrate:
                audio_bitrate = min_audio_bitrate
            elif audio_bitrate > max_audio_bitrate:
                audio_bitrate = max_audio_bitrate

        # Target video bitrate, in bps.
        video_bitrate = target_total_bitrate - audio_bitrate
        if video_bitrate < 1000:
            print(
                "%s Bitrate %s is extremely low! Stop compress.",
                datetime.fromtimestamp(time.time()).strftime("%Y%m%d%H%M%S"),
                video_bitrate,
            )
            return False

        i = ffmpeg.input(video_full_path)
        if two_pass:
            ffmpeg.output(
                i,
                os.devnull,
                **{"c:v": "libx264", "b:v": video_bitrate, "pass": 1, "f": "mp4"},
            ).overwrite_output().run()
            ffmpeg.output(
                i,
                output_file_name,
                **{
                    "c:v": "libx264",
                    "b:v": video_bitrate,
                    "pass": 2,
                    "c:a": "aac",
                    "b:a": audio_bitrate,
                },
            ).overwrite_output().run()
        else:
            ffmpeg.output(
                i,
                output_file_name,
                **{
                    "c:v": "libx264",
                    "b:v": video_bitrate,
                    "c:a": "aac",
                    "b:a": audio_bitrate,
                },
            ).overwrite_output().run()

        if os.path.getsize(output_file_name) <= size_upper_bound * 1024:
            print(
                "%s Compressed video: %s",
                datetime.fromtimestamp(time.time()).strftime("%Y%m%d%H%M%S"),
                output_file_name,
            )
            return output_file_name
        elif os.path.getsize(output_file_name) < os.path.getsize(
            video_full_path
        ):  # Do it again
            print(
                "%s Compressed video: %s",
                datetime.fromtimestamp(time.time()).strftime("%Y%m%d%H%M%S"),
                output_file_name,
            )
            return compress_video(output_file_name, size_upper_bound)
        else:
            return False
    except FileNotFoundError:
        print(
            "%s You do not have ffmpeg installed!",
            datetime.fromtimestamp(time.time()).strftime("%Y%m%d%H%M%S"),
        )
        print(
            "%s You can install ffmpeg by reading https://github.com/kkroening/ffmpeg-python/issues/251",
            datetime.fromtimestamp(time.time()).strftime("%Y%m%d%H%M%S"),
        )
        return False


def compress_if_needed(filename):
    """Compress and upload video to GCS"""

    original_size = os.path.getsize(filename) / 1024

    if original_size <= 9500:
        print(
            "%s File size is already under 9MB, no need to compress.",
            datetime.fromtimestamp(time.time()).strftime("%Y%m%d%H%M%S"),
        )
    else:
        compress_video(filename, 9500)

    return filename


def upload_blob(storage_client, bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # The ID of your GCS bucket
    # The path to your file to upload
    # The ID to give your file on GCS
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)


def save_to_google_cloud(tmp_file, filename):
    print("Saving %s to GCP..." % (tmp_file))
    credentials = service_account.Credentials.from_service_account_file(
        "/tmp/google_auth.json"
    )

    storage_client = storage.Client(credentials=credentials)
    upload_blob(
        storage_client,
        bucket_name=os.getenv("GOOGLE_BLOB"),
        source_file_name=tmp_file,
        destination_blob_name=filename,
    )
    print("Successfully uploaded to: %s" % ("gs://notion3000/" + filename))
    # Return data for use in future steps
    return "gs://notion3000/" + filename


def get_video_summary(filename):
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
            """Your task is to create a comprehensive summary of this video that includes:
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
            generative_models.Part.from_uri(filename, mime_type="video/mp4"),
        ],
        stream=True,
    )

    final = ""
    for chunk in response:
        final += chunk.text
    return final


def parse_html_tags(input_string):
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
    print("Running video pipeline...")
    filename = pd.steps["trigger"]["event"]["body"]["filename"]
    filepath = pd.steps["trigger"]["event"]["body"]["filepath"]
    tmp_file = "/tmp/" + filename

    print("Compressing...")
    compress_if_needed(tmp_file)
    # Return data for use in future steps
    print("Compress done - uploading to GCP...")
    gcp_file = save_to_google_cloud(tmp_file, filename)
    summary = get_video_summary(gcp_file)
    html_parse = parse_html_tags(summary)
    notion_url = config.save_to_notion(html_parse)
    return {"url": notion_url}
