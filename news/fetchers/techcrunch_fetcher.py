import requests
import datetime
import feedparser
from bs4 import BeautifulSoup
from django.db import IntegrityError, transaction
from news.models import RawNews
from news.management.sources.fetch_or_create_source import fetch_or_create_source


TECHCRUNCH_FEEDS = {
    "Apps": "https://techcrunch.com/apps/feed/",
    "Startups": "https://techcrunch.com/startups/feed/",
}


def fetch_full_techcrunch_article(url):
    """Fetch full article content and featured image from TechCrunch article page."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Collect all article paragraphs
        paragraphs = [p.get_text(" ", strip=True)
                      for p in soup.select("p.wp-block-paragraph")]
        full_text = "\n\n".join(paragraphs) if paragraphs else ""

        # Get featured image
        img_tag = soup.select_one("figure.wp-block-post-featured-image img")
        img_url = img_tag["src"] if img_tag and img_tag.has_attr("src") else ""

        return full_text, img_url

    except requests.RequestException as e:
        print(f"[ERROR] Could not fetch TechCrunch article {url}: {e}")
        return "", ""


def fetch_techcrunch(feed_name="Apps", limit=10):
    """Fetch and store TechCrunch RSS feed articles in RawNews with full content."""
    feed_url = TECHCRUNCH_FEEDS.get(feed_name)
    if not feed_url:
        print(f"[ERROR] Unknown TechCrunch feed: {feed_name}")
        return

    try:
        response = requests.get(feed_url, timeout=10)
        response.raise_for_status()
        parsed_feed = feedparser.parse(response.content)
        entries = parsed_feed.entries[:limit]
    except requests.RequestException as e:
        print(f"[ERROR] Could not fetch TechCrunch {feed_name} feed: {e}")
        return

    source = fetch_or_create_source(
        name=f"TechCrunch {feed_name}",
        url="https://techcrunch.com/",
        icon_url="https://techcrunch.com/wp-content/uploads/2018/07/cropped-cropped-tc-favicon.png?w=192",
    )

    for entry in entries:
        try:
            source_news_id = entry.get("id") or entry.get(
                "guid") or entry.get("link")

            with transaction.atomic():
                existing = RawNews.objects.filter(
                    source_news_id=source_news_id, source=source
                ).first()

                if existing and existing.status == "processed":
                    continue

            # Fetch full article text from link
            full_content, img_url = fetch_full_techcrunch_article(
                entry.get("link", ""))

            RawNews.objects.update_or_create(
                source_news_id=source_news_id,
                source=source,
                defaults={
                    "title": entry.get("title", ""),
                    "description": full_content or entry.get("summary", ""),
                    "url": entry.get("link", ""),
                    "source_url": entry.get("link", ""),
                    "published_at": datetime.datetime.fromtimestamp(
                        datetime.datetime(
                            *entry.published_parsed[:6]).timestamp(),
                        tz=datetime.timezone.utc,
                    )
                    if hasattr(entry, "published_parsed")
                    else datetime.datetime.now(datetime.timezone.utc),
                    "fetched_at": datetime.datetime.now(datetime.timezone.utc),
                    "status": "raw",
                    "img_url": img_url,
                },
            )

        except IntegrityError as e:
            print(
                f"[DB ERROR] Failed to save TechCrunch article {entry.get('id')}: {e}")
        except Exception as e:
            print(
                f"[ERROR] Unexpected error for TechCrunch article {entry.get('id')}: {e}")
