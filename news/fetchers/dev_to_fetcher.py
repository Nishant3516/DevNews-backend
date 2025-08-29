import requests
import datetime
from django.db import IntegrityError
from news.models import RawNews
from decouple import config
from news.management.sources.fetch_or_create_source import fetch_or_create_source

DEVTO_BASEURL = config("DEVTO_BASEURL", default="https://dev.to/api/")
DEVTO_ARTICLES_URL = f"{DEVTO_BASEURL}articles"


def fetch_top_devto_articles(limit=10):
    """Fetch top latest Dev.to articles."""
    try:
        params = {"per_page": limit}
        response = requests.get(DEVTO_ARTICLES_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"[ERROR] Could not fetch dev.to articles: {e}")
        return []


def fetch_full_devto_article(article_id):
    """Fetch full article details from Dev.to by ID."""
    try:
        url = f"{DEVTO_ARTICLES_URL}/{article_id}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"[ERROR] Could not fetch full article {article_id}: {e}")
        return None


def fetch_devto(limit=10):
    """Fetch and store Dev.to articles in RawNews with full content."""
    articles = fetch_top_devto_articles(limit)
    if not articles:
        return

    source = fetch_or_create_source(
        name="Dev.to",
        url="https://dev.to/",
        icon_url="https://d2fltix0v2e0sb.cloudfront.net/dev-black.png",
    )

    for article in articles:
        try:
            if not article or "id" not in article:
                continue

            # Fetch full article details
            full_article = fetch_full_devto_article(article["id"])
            if not full_article:
                continue

            RawNews.objects.update_or_create(
                source_news_id=str(article["id"]),
                source=source,
                defaults={
                    "title": article.get("title", ""),
                    "description": full_article.get("body_markdown") or article.get("description") or "",
                    "url": article.get("url", ""),
                    "source_url": f"{DEVTO_ARTICLES_URL}/{article['id']}",
                    "published_at": datetime.datetime.fromisoformat(
                        article.get("published_timestamp").replace(
                            "Z", "+00:00")
                    )
                    if article.get("published_timestamp")
                    else datetime.datetime.now(datetime.timezone.utc),
                    "fetched_at": datetime.datetime.now(datetime.timezone.utc),
                    "status": "raw",
                    "img_url": article.get("cover_image", ""),
                },
            )

        except IntegrityError as e:
            print(
                f"[DB ERROR] Failed to save article {article.get('id')}: {e}")
        except Exception as e:
            print(
                f"[ERROR] Unexpected error for article {article.get('id')}: {e}")
