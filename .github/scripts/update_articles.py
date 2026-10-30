"""Rewrites the latest-articles list in README.md from the SwiftyJourney RSS feed."""

import email.utils
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET

FEED_URL = "https://swiftyjourney.com/rss.xml"
README = "README.md"
COUNT = 5
# Cloudflare rejects urllib's default user agent.
USER_AGENT = "jfdoradotr-profile-readme (+https://github.com/jfdoradotr/jfdoradotr)"
START = "<!-- ARTICLES:START -->"
END = "<!-- ARTICLES:END -->"


def latest_articles():
    request = urllib.request.Request(FEED_URL, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        root = ET.fromstring(response.read())
    items = [
        (
            email.utils.parsedate_to_datetime(item.findtext("pubDate")),
            item.findtext("title").strip(),
            item.findtext("link").strip(),
        )
        for item in root.iter("item")
    ]
    items.sort(reverse=True)
    return [f"- [{title}]({link})" for _, title, link in items[:COUNT]]


def main():
    articles = latest_articles()
    if not articles:
        sys.exit("The feed has no items; leaving README.md as it is.")

    with open(README, encoding="utf-8") as file:
        readme = file.read()
    block = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    if not block.search(readme):
        sys.exit(f"README.md has no {START} … {END} block.")

    updated = block.sub(lambda _: "\n".join([START, *articles, END]), readme)
    with open(README, "w", encoding="utf-8") as file:
        file.write(updated)


if __name__ == "__main__":
    main()
