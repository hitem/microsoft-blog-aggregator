#!/usr/bin/env python3
# Auth: hitem

import asyncio
import aiohttp
import feedparser
from lxml import etree
import datetime
import os
from bs4 import BeautifulSoup

# Set to True for appending, False for overwriting
append_mode = False
# Set the maximum age for entries in days when in append mode
max_age_days = 365

# Define the list of RSS feed URLs
rss_feed_urls = [
    "https://techcommunity.microsoft.com/t5/s/gxcuf89792/rss/board?board.id=MicrosoftSecurityandCompliance",
    "https://techcommunity.microsoft.com/t5/s/gxcuf89792/rss/board?board.id=Identity",
    "https://techcommunity.microsoft.com/t5/s/gxcuf89792/rss/board?board.id=CoreInfrastructureandSecurityBlog",
    "https://techcommunity.microsoft.com/t5/s/gxcuf89792/rss/board?board.id=AzureNetworkSecurityBlog",
    "https://techcommunity.microsoft.com/t5/s/gxcuf89792/rss/board?board.id=MicrosoftThreatProtectionBlog",
    "https://techcommunity.microsoft.com/t5/s/gxcuf89792/rss/board?board.id=MicrosoftDefenderCloudBlog",
    "https://techcommunity.microsoft.com/t5/s/gxcuf89792/rss/board?board.id=MicrosoftDefenderATPBlog",
    "https://techcommunity.microsoft.com/t5/s/gxcuf89792/rss/board?board.id=MicrosoftDefenderIoTBlog",
    "https://techcommunity.microsoft.com/t5/s/gxcuf89792/rss/board?board.id=DefenderExternalAttackSurfaceMgmtBlog",
    "https://techcommunity.microsoft.com/t5/s/gxcuf89792/rss/board?board.id=Vulnerability-Management",
    "https://techcommunity.microsoft.com/t5/s/gxcuf89792/rss/board?board.id=DefenderThreatIntelligence",
    "https://techcommunity.microsoft.com/t5/s/gxcuf89792/rss/board?board.id=MicrosoftSecurityExperts",
    "https://techcommunity.microsoft.com/t5/s/gxcuf89792/rss/board?board.id=Microsoft-Security-Baselines",
    "https://techcommunity.microsoft.com/t5/s/gxcuf89792/rss/board?board.id=MicrosoftSentinelBlog",
    "https://techcommunity.microsoft.com/t5/s/gxcuf89792/rss/board?board.id=MicrosoftDefenderforOffice365Blog",
]

# Set the output file name
output_file = "aggregated_feed.xml"
processed_links_file = "processed_links.txt"

# Define the time threshold
recent_time_threshold = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=2)

# Read previously processed links
try:
    with open(processed_links_file, "r") as f:
        processed_links = set(line.split()[1] for line in f if line.strip())
except FileNotFoundError:
    processed_links = set()

# Asynchronous function to fetch RSS feed content
async def fetch_rss_feed(url, session):
    try:
        async with session.get(url, timeout=10) as response:
            if response.status == 200:
                content = await response.text()
                return feedparser.parse(content)
            else:
                print(f"Error fetching {url}: HTTP {response.status}")
                return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

# Main asynchronous function to process RSS feeds
async def process_feeds():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_rss_feed(url, session) for url in rss_feed_urls]
        feeds = await asyncio.gather(*tasks)

        # Filter out None results
        all_entries = []
        for feed in feeds:
            if feed and feed.entries:
                all_entries.extend(feed.entries)

        # Remove duplicates and already processed links
        unique_entries = [
            entry for entry in all_entries if entry.link not in processed_links
        ]

        # Filter recent entries
        recent_entries = [
            entry for entry in unique_entries
            if datetime.datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %Z").replace(tzinfo=datetime.timezone.utc) >= recent_time_threshold
        ]

        # Sort entries
        sorted_entries = sorted(
            recent_entries, key=lambda x: x.published_parsed, reverse=True)
        update_feed(sorted_entries)

# Function to update or create the XML feed
def update_feed(sorted_entries):
    now = datetime.datetime.now(datetime.timezone.utc)

    if append_mode and os.path.exists(output_file):
        # Load existing feed
        tree = etree.parse(output_file)
        root = tree.getroot()
        channel = root.find("channel")
    else:
        # Create a new feed structure
        root = etree.Element("rss", version="2.0")
        channel = etree.SubElement(root, "channel")
        etree.SubElement(channel, "title").text = "RSS Aggregator Feed"
        etree.SubElement(
            channel, "link").text = "https://hitem.github.io/rss-aggregator/aggregated_feed.xml"
        etree.SubElement(
            channel, "description").text = "An aggregated feed of Microsoft blogs"

    # Update lastBuildDate
    last_build_date = channel.find("lastBuildDate")
    if last_build_date is None:
        last_build_date = etree.SubElement(channel, "lastBuildDate")
    last_build_date.text = now.strftime("%a, %d %b %Y %H:%M:%S GMT")

    # Add new entries to the feed
    for entry in sorted_entries:
        item = etree.SubElement(channel, "item")
        etree.SubElement(item, "title").text = entry.title
        etree.SubElement(item, "link").text = entry.link
        etree.SubElement(item, "pubDate").text = entry.published
        etree.SubElement(item, "guid", isPermaLink="false").text = entry.id if hasattr(
            entry, "id") else entry.link
        soup = BeautifulSoup(entry.summary, "lxml")
        summary_text = soup.get_text()
        limited_summary = summary_text[:600] + \
            "..." if len(summary_text) > 350 else summary_text
        etree.SubElement(item, "description").text = limited_summary

    # Write updated feed to file
    with open(output_file, "wb") as f:
        f.write(etree.tostring(root, pretty_print=True))

    # Update processed links
    with open(processed_links_file, "a") as f:
        for entry in sorted_entries:
            timestamp = datetime.datetime.strptime(
                entry.published, "%a, %d %b %Y %H:%M:%S %Z").strftime("%Y-%m-%dT%H:%M:%S")
            f.write(f"{timestamp} {entry.link}\n")

    # Output RSS feed entry count
        if "GITHUB_ENV" in os.environ:
            with open(os.environ["GITHUB_ENV"], "a") as f:
                f.write(f"RSS_FEED_ENTRIES={len(sorted_entries)}\n")
        else:
            print(f"RSS_FEED_ENTRIES={len(sorted_entries)}")  # For local testing

# Run the async main function
asyncio.run(process_feeds())
