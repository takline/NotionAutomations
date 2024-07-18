
# Introduction to Python Scripts for Enhanced Productivity and Automation

This collection of Python scripts is designed to significantly enhance productivity and automate routine tasks involving content summarization, video processing, and task notification management. Each script is tailored for specific use cases, leveraging cutting-edge technology and seamless integration with popular services like Notion, AWS, Google Cloud Platform, and Pushover.

Each script is designed with extensibility and ease of use in mind, catering to developers, content creators, and productivity enthusiasts seeking to automate and streamline their workflows.


## 1. **URL Information Extractor and Summarizer to Notion (`links.py`)**

This script automates the extraction of key information from URLs, summarizes web content using advanced language models, and saves these summaries to a Notion database. It's perfect for content curation, competitive analysis, and knowledge management.

### Key Features:
- Automated URL data extraction and summarization.
- Integration with Notion for organized content storage.
- Custom scraper extensions for diverse web sources.

<details>

<summary>Open full README.md for links.py</summary>


##  URL Information Extractor and Summarizer to Notion - Overview
This module is designed to extract information from URLs, retrieve page text, and scrape data based on the company associated with the URL. It extends link processing to include summarizing content using a complex language model (LangChainLLM) and saving summaries to a Notion database. This tool is ideal for content aggregation, analysis, and documentation purposes.

## Features
- Extracts key information from URLs, including company name and page ID.
- Summarizes web page content using the LangChainLLM language model.
- Creates a new page in Notion with the summary, key points, and tags.

## Prerequisites
Before you begin, ensure you have the following installed:
- Python 3.6 or later
- Required Python packages: `requests`, `beautifulsoup4`, `langchainllm` (hypothetical), and any other dependencies for the custom scrapers (`Instagram`, `Threads`, `Twitter`, `YouTube`).

Additionally, you'll need:
- API keys and access tokens for Notion and any other services used by the scrapers.
- A Notion database set up to receive the summaries.

## Installation
1. Clone this repository to your local machine.
2. Install the required Python packages:
   ```
   pip install requests beautifulsoup4
   ```
   Install other dependencies as required by your environment or the specific scrapers you intend to use.

3. Configure the `config.py` file with your API keys, tokens, and database IDs.

## Usage
To use this module, you'll typically call the `process_link` method with a URL. Here's a simple example:

```python
from enhanced_link_processor import EnhancedLinkProcessor

processor = EnhancedLinkProcessor()
notion_page_url = processor.process_link("https://example.com/some-page")
print(f"Notion page created: {notion_page_url}")
```

## Configuration
The module requires several configurations to interact with external services:
- **Notion Integration**: Set up an integration on Notion's Developer Portal and share your database with this integration. Provide the integration token and database ID in `config.py`.
- **Language Model Setup**: If using a custom or third-party language model, ensure it's correctly configured and authenticated as needed.

## Custom Scrapers
This module supports extending or customizing scrapers for different websites. Each scraper should implement a method `get_data(page_id)` that returns structured data from the page.

## Contributing
Contributions to this project are welcome. Please follow standard pull request and code review practices. Ensure any new dependencies or services are well documented.

## License
This work is shared under MIT, ensuring it is accessible and reusable under certain conditions.


</details>


## 2. **Video Summarizer to Notion (`video_summarize.py`)**

`video_summarize.py` streamlines the process of video content summarization and storage. By compressing videos, uploading them to Google Cloud Storage, and generating summaries through Vertex AI, it creates accessible and insightful video content summaries directly in Notion.

### Key Features:
- Video compression and Google Cloud Storage integration.
- AI-powered content summarization.
- Notion integration for summary storage and access.

<details>

<summary>Open full README for video_summarize.py</summary>

## Video Summarizer to Notion - Overview

`video_summarize.py` is a Python script designed for compressing videos, uploading them to Google Cloud Storage (GCS), and generating a comprehensive summary of the video content using Vertex AI's Generative Model. This script is particularly useful for creating condensed and insightful representations of video data, which can be utilized for various applications such as content analysis, media management, and quick information retrieval.

## Prerequisites

Before you begin, ensure you have the following prerequisites:

- Python 3.6 or later.
- Access to Google Cloud Platform (GCP) with billing enabled.
- A GCP bucket for storing videos.
- Google Cloud Storage and Vertex AI API enabled on your GCP project.
- A service account with permissions to access Cloud Storage and Vertex AI, and a JSON key file for authentication.

## Installation

1. Clone the repository to your local machine.

2. Install the required Python packages:

   ```bash
   pip install ffmpeg-python google-cloud-storage google-cloud-aiplatform requests
   ```

3. Set up your GCP credentials by placing your service account JSON key file in a known directory and setting an environment variable to its path:

   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-file.json"
   ```

4. Set the necessary environment variables for your Google Cloud setup:

   ```bash
   export GOOGLE_PROJECT_ID="your-google-cloud-project-id"
   export GOOGLE_LOCATION="your-google-cloud-project-location"
   export GOOGLE_BLOB="your-google-cloud-storage-bucket-name"
   ```

## Configuration

Modify the script to include your specific GCP project details, bucket names, and any other preferences. You may need to adjust parameters such as bitrate thresholds or output formats according to your requirements.

## Usage

The script `video_summarize.py` consists of several functions that together facilitate the process of video compression, uploading, and summarization. Here's how to use it:

1. **Compress Video**: Automatically compresses videos that exceed a specific size threshold.

2. **Upload to GCS**: Uploads the compressed video to a specified Google Cloud Storage bucket.

3. **Generate Video Summary**: Utilizes Vertex AI's Generative Model to generate a summary of the video content.

4. **Handler Function**: Orchestrates the process from receiving a video file, compressing it, uploading it to GCS, generating a summary, and potentially integrating with additional services (e.g., saving summaries to a database or a platform like Notion).

To run the script:

```bash
python video_summarize.py
```

Ensure that you have an appropriate mechanism to trigger the script, such as a webhook or a scheduled task, depending on your application's architecture.

## Troubleshooting

- **ffmpeg not found**: Ensure ffmpeg is installed and accessible in your system's PATH, or refer to the installation guide provided in the script comments.
- **Google Cloud Authentication Issues**: Verify your service account permissions, ensure the JSON key file's path is correctly set, and check if the environment variables are correctly configured.
- **Vertex AI API Errors**: Confirm that the Vertex AI API is enabled for your project and that your service account has the necessary roles assigned.

## Contributing

Contributions to improve `video_summarize.py` are welcome. Please follow the standard fork-pull request workflow.

1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -am 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a pull request.

## License

This work is shared under MIT, ensuring it is accessible and reusable under certain conditions.


</details>

## 3. **NotionGPT Notification System (`task_reminders.py`)**

This system is engineered to send notifications for tasks managed in Notion, utilizing AWS Secrets Manager for secure information storage and Pushover for notification delivery. It efficiently organizes and reminds users of due, upcoming, and late tasks.

### Key Features:
- Secure secrets management with AWS.
- Pushover integration for immediate task notifications.
- Customizable task processing tailored to user workflow.


<details>

<summary>Open full README for task_reminders.py </summary>


## NotionGPT Notification System - Overview

This project provides a system for sending notifications for tasks managed in Notion. It leverages AWS Secrets Manager for secure storage of sensitive information, and the Pushover service for sending the notifications. The system identifies tasks due today, upcoming tasks, and late tasks, and notifies the user accordingly.

## Getting Started

### Prerequisites

- Python 3.x
- `boto3` library for AWS services
- An AWS account with access to Secrets Manager
- A Pushover account for sending notifications
- Notion integration to manage tasks

### Installation

1. Ensure Python 3.x is installed on your system.
2. Install `boto3` using pip:
   ```sh
   pip install boto3
   ```
3. Set up your AWS credentials to enable access to Secrets Manager. This typically involves configuring your `~/.aws/credentials` file or setting environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`).

### Configuration

1. Store your Pushover `app_token` and `user_key`, along with any other necessary secrets, in AWS Secrets Manager. The default secret name is `notionGPT`, but this can be configured via environment variables.
2. Set the following environment variables as needed:
   - `NOTION_GPT_SECRET_NAME`: The name of the secret in AWS Secrets Manager (default: `notionGPT`).
   - `AWS_REGION`: The AWS region where your secrets are stored (default: `us-east-1`).

### Usage

To use this system, execute the main script and ensure that your Notion tasks are structured in a way that they can be processed by the script. You'll need to adapt the `handler` function to your specific Notion setup, particularly how tasks are categorized as today, upcoming, or late.

### Code Structure

- **SecretsManager**: Handles retrieval of secrets from AWS Secrets Manager.
- **NotificationSender**: Sends notifications via Pushover based on task details.
- **process_tasks**: Processes lists of tasks and sends notifications for each task, with a delay between notifications to avoid rate limits.
- **handler**: The main entry point of the script. It retrieves secrets, processes tasks according to their due status, and manages timing for notifications.

## Development

- Extend or modify the task processing logic in `handler` to fit your Notion task management workflow.
- Adjust notification details and payload in `NotificationSender` as needed for your use case.
- Ensure to handle errors and exceptions, especially for network requests and AWS service access.

## Contributing

Contributions are welcome. Please open an issue or submit a pull request with your proposed changes or improvements.

## License

This work is shared under MIT, ensuring it is accessible and reusable under certain conditions.


</details>

