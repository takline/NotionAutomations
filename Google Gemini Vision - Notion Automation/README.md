### Video --> Notion --> Google Gemini Summary --> Notion

#### **Overview**

This repository contains a Python application designed to create automated summaries of videos saved to the iOS Notion app. The application integrates Notion, Google Cloud Platform (GCP), and Google's Gemini multimodal Large Language Model (LLM) to fetch videos from Notion, optionally compress them, and then generate summaries using advanced AI techniques. The summarized content is formatted in HTML for easy integration back into Notion or other platforms.

---

#### **Components**

1. **Notion Integration:** Interacts with a Notion database to retrieve videos.

2. **Video Processing:** Compresses videos if they exceed a specified size limit.

3. **Google Cloud Storage:** Uploads the processed videos to Google Cloud for further processing.

4. **Google's Gemini Model:** Utilizes this cutting-edge AI model to generate summaries of the videos.

5. **Pipedream Workflow:** Orchestrates the entire process, triggered when a new note with a video is created in Notion.

---

#### **Setup and Configuration**

1. **Prerequisites:**
   - Python 3.8 or later.
   - Access to Google Cloud Platform and a configured GCP bucket.
   - A Notion account with API access.
   - Pipedream account for workflow automation.

2. **Environment Setup:**
   - Install required Python packages: `ffmpeg-python`, `moviepy`, `google-cloud-aiplatform`.
   - Set environment variables for Google Cloud credentials and Notion API access.

3. **Google Cloud Credentials:**
   - Follow Google Cloud documentation to obtain service account credentials.
   - Update the credentials in the script or set them as environment variables.

4. **Notion Setup:**
   - Create a Notion database with video attachments.
   - Obtain API access and integrate it with the script.

5. **Pipedream Workflow:**
   - Set up a Pipedream workflow that triggers the script when a new video note is created in Notion.

---

#### **Usage**

- **Running the Script:**
  The script can be executed as part of the Pipedream workflow. On triggering, it performs the following steps:
  1. Downloads the video from Notion.
  2. Checks and compresses the video if it's larger than the specified limit.
  3. Uploads the video to Google Cloud Storage.
  4. Sends the video to Google's Gemini model for summarization.
  5. The summary is then parsed and can be used to update the Notion note or for other purposes.

- **Customization:**
  You can customize the script to change the compression settings, summary format, or integrate with different platforms.

---

#### **Gemini Model Overview**

Google's Gemini model is a state-of-the-art multimodal Large Language Model capable of understanding and generating content from both text and media inputs like videos. In this application, Gemini analyzes the video content and generates a comprehensive summary, demonstrating its ability to handle complex AI tasks.

---

#### **Contributing**

Contributions to this project are welcome. Please follow the standard GitHub pull request process to submit your changes.

---

#### **License**

This project is released under MIT License, allowing for both personal and commercial use with proper attribution.

---

#### **Contact**

For any queries or collaboration requests, please reach out to tylerkline@gmail.com.

---

### **Note:**

This README provides a high-level overview of the application, its components, and usage. It's designed to cater to both technical and non-technical audiences, ensuring clarity in understanding the project's functionality and scope.