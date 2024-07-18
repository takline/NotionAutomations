"""
This module provides functionality to extract information from URLs,
retrieve page text, and scrape data based on the company associated with the URL.
"""
import json
import logging
import os
import re
import time
import urllib.parse
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from langchainllm import LangChainLLM
from scrapers import Instagram, Threads, Twitter, YouTube


class EnhancedLinkProcessor:
    """
    Extends link processing to include extracting information, summarizing with a language model,
    and saving to a Notion database.
    """

    def __init__(self):
        self.lang_model = LangChainLLM()  # Initialize the language model

    def process_link(self, url):
        """
        Process the given URL to extract information, generate a summary, and save to Notion.

        :param url: The URL to process.
        :return: URL of the created Notion page.
        """
        # Step 1: Use existing functionality to get link data
        link_text = get_link_data(url)

        # Step 2: Use the LangChainLLM to analyze and summarize the link text
        summary_content = self.lang_model.summarize(link_text)

        # Step 3: Create a new Notion page with the summary
        notion_page_url = create_notion_page(summary_content)

        return notion_page_url


def create_notion_page(summary_content):
    """Create a new page in Notion based on the summary content."""
    response = config.NOTION_CLIENT.pages.create(
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
    logging.info(
        "%s Created Notion page: %s",
        datetime.fromtimestamp(time.time()).strftime("%Y%m%d%H%M%S"),
        summary_content["TITLE"],
    )

    return response["url"]


def get_page_text(url):
    """
    Retrieves the text of a webpage given its URL.

    :param url: The URL of the webpage.
    :return: Text content of the webpage or error message.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.get_text()
    except requests.RequestException as e:
        return str(e)


def parse_url(url):
    """
    Parses the given URL and extracts the domain and path.

    :param url: The URL to parse.
    :return: Parsed domain and path.
    """
    parsed_url = urllib.parse.urlparse(url)
    domain = parsed_url.netloc
    path = parsed_url.path
    return domain, path


def map_domain_to_company(domain):
    """
    Maps domain to company name using a direct lookup dictionary.

    :param domain: The domain to map.
    :return: Mapped company name or "N/A" if not found.
    """
    domain_company_map = {
        "instagram": "Instagram",
        "threads.": "Threads",
        "youtube": "YouTube",
        "x.com": "Twitter",
        "twitter": "Twitter",
    }
    for key in domain_company_map:
        if key in domain:
            return domain_company_map[key]
    return "N/A"


def extract_page_id(domain, path, query):
    """
    Extracts the page ID from the URL path or query parameters.

    :param domain: The domain of the URL.
    :param path: The path of the URL.
    :param query: The query of the URL.
    :return: Extracted page ID.
    """
    if domain == "youtube.com":
        query_params = urllib.parse.parse_qs(query)
        return query_params.get("v", [None])[0]
    else:
        path_parts = path.strip("/").split("/")
        return path_parts[-1]


def get_link_data(url):
    """
    Extracts data from a link based on the associated company.

    :param url: The URL to extract data from.
    :return: Extracted data or webpage text as fallback.
    """
    domain, path = parse_url(url)[:2]
    company = map_domain_to_company(domain)
    page_id = extract_page_id(domain, path, urllib.parse.urlparse(url).query)

    if company == "Threads":
        scraper = Threads()
    elif company == "Twitter":
        scraper = Twitter()
    elif company == "Instagram":
        scraper = Instagram()
    elif company == "YouTube":
        scraper = YouTube()
    else:
        return get_page_text(url)

    return scraper.get_data(page_id)


def handler(pd):
    """
    Handler function to process URLs and extract link data.

    :param pd: Pipedream context or similar context object.
    :return: Extracted link data.
    """
    url = pd.steps["trigger"]["event"]["properties"]["URL"]["url"]
    link_data = get_link_data(url)
    return link_data
