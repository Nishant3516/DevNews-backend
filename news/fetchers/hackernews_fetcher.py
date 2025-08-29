import requests
import datetime
from django.db import IntegrityError
from news.models import RawNews
from decouple import config
from news.management.sources.fetch_or_create_source import fetch_or_create_source

HACKERNEWS_BASEURL = config("HACKERNEWS_BASEURL")
HACKERNEWS_TOPSTORIES_URL = f"{HACKERNEWS_BASEURL}topstories.json"


def fetch_top_story_ids(limit=10):
    """Fetch top Hacker News story IDs."""
    try:
        response = requests.get(HACKERNEWS_TOPSTORIES_URL, timeout=10)
        response.raise_for_status()
        return response.json()[:limit]
    except requests.RequestException as e:
        print(f"[ERROR] Could not fetch top stories: {e}")
        return []


def fetch_hackernews(limit=10):
    """Fetch and store Hacker News stories in RawNews."""
    story_ids = fetch_top_story_ids(limit)
    if not story_ids:
        return

    source = fetch_or_create_source(
        name="Hacker News",
        url="https://news.ycombinator.com/",
        icon_url="https://news.ycombinator.com/favicon.ico",
    )

    for story_id in story_ids:
        try:
            story_url = f"{HACKERNEWS_BASEURL}item/{story_id}.json"
            response = requests.get(story_url, timeout=10)
            response.raise_for_status()
            article = response.json()

            if not article or "title" not in article:
                continue

            RawNews.objects.update_or_create(
                source_news_id=str(article["id"]),
                source=source,
                defaults={
                    "title": article.get("title", ""),
                    "description": article.get("text") or "",
                    "url": article.get("url") or f"https://news.ycombinator.com/item?id={story_id}",
                    "source_url": story_url,
                    "published_at": datetime.datetime.fromtimestamp(
                        article.get(
                            "time", datetime.datetime.now().timestamp()),
                        tz=datetime.timezone.utc,
                    ),
                    "fetched_at": datetime.datetime.now(datetime.timezone.utc),
                    "status": "raw",
                },
            )

        except requests.RequestException as e:
            print(f"[ERROR] Failed to fetch story {story_id}: {e}")
        except IntegrityError as e:
            print(f"[DB ERROR] Failed to save story {story_id}: {e}")
        except Exception as e:
            print(f"[ERROR] Unexpected error for story {story_id}: {e}")
