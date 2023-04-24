#!/usr/bin/env python3
# Auth: hitem

import feedparser
from lxml import etree
import datetime
import os
from bs4 import BeautifulSoup

# Define the list of RSS feed URLs
rss_feed_urls = [
    "https://techcommunity.microsoft.com/gxcuf89792/rss/board?board.id=MicrosoftSecurityandCompliance",
    "https://techcommunity.microsoft.com/gxcuf89792/rss/board?board.id=Identity",
    "https://techcommunity.microsoft.com/gxcuf89792/rss/board?board.id=CoreInfrastructureandSecurityBlog",
    "https://techcommunity.microsoft.com/gxcuf89792/rss/board?board.id=AzureNetworkSecurityBlog",
    "https://techcommunity.microsoft.com/gxcuf89792/rss/board?board.id=IdentityStandards",
    "https://techcommunity.microsoft.com/gxcuf89792/rss/board?board.id=MicrosoftThreatProtectionBlog",
    "https://techcommunity.microsoft.com/gxcuf89792/rss/board?board.id=MicrosoftDefenderCloudBlog",
    "https://techcommunity.microsoft.com/gxcuf89792/rss/board?board.id=MicrosoftDefenderATPBlog",
    "https://techcommunity.microsoft.com/gxcuf89792/rss/board?board.id=MicrosoftDefenderIoTBlog",
]

# Set the output file name
output_file = "aggregated_feed.xml"

# Read previously processed links
with open("processed_links.txt", "r") as f:
    processed_links = set(f.read().splitlines())

# Parse and aggregate the RSS feeds
all_entries = []
for url in rss_feed_urls:
    feed = feedparser.parse(url)
    all_entries.extend(feed.entries)

# Remove duplicates based on the 'link' field and filter out already processed links
unique_entries = [entry for entry in all_entries if entry.link not in processed_links]

# Filter entries published within the last 60 days
time_threshold = datetime.datetime.utcnow() - datetime.timedelta(hours=6)
recent_entries = [entry for entry in unique_entries if datetime.datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %Z") >= time_threshold]

# Sort entries by published date in descending order
sorted_entries = sorted(recent_entries, key=lambda x: x.published_parsed, reverse=True)

# Create a new XML tree for the aggregated RSS feed
root = etree.Element("rss", version="2.0")
channel = etree.SubElement(root, "channel")
etree.SubElement(channel, "title").text = "RSS Aggregator Feed"
etree.SubElement(channel, "link").text = "https://hitem.github.io/rss-aggregator/aggregated_feed.xml"
etree.SubElement(channel, "description").text = "An aggregated feed of Microsoft blogs"
etree.SubElement(channel, "lastBuildDate").text = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")

# Add entries to the new feed
for entry in sorted_entries:
    item = etree.SubElement(channel, "item")
    etree.SubElement(item, "title").text = entry.title
    etree.SubElement(item, "link").text = entry.link
    etree.SubElement(item, "pubDate").text = entry.published
    etree.SubElement(item, "guid", isPermaLink="false").text = entry.id if hasattr(entry, "id") else entry.link
    # Change number depending on how many characters you want to include
    soup = BeautifulSoup(entry.summary, "lxml")
    summary_text = soup.get_text()
    limited_summary = summary_text[:600] + "..." if len(summary_text) > 350 else summary_text
    etree.SubElement(item, "description").text = limited_summary


# Write the output to a file
with open(output_file, "wb") as f:
    f.write(etree.tostring(root, pretty_print=True))

# Update the processed links file with new links
with open("processed_links.txt", "a") as f:
    for entry in recent_entries:
        f.write(f"{entry.link}\n")

# Set the RSS_FEED_ENTRIES environment variable
with open(os.environ["GITHUB_ENV"], "a") as f:
    f.write(f"RSS_FEED_ENTRIES={len(sorted_entries)}\n")