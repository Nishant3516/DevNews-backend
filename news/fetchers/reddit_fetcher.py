import requests
import datetime
from django.db import IntegrityError
from decouple import config
from news.models import RawNews
from news.management.sources.fetch_or_create_source import fetch_or_create_source

# --- Config ---
REDDIT_BASEURL = config("REDDIT_BASEURL", default="https://oauth.reddit.com")
REDDIT_SUBREDDIT = config("REDDIT_SUBREDDIT", default="programming")
REDDIT_LIMIT = config("REDDIT_LIMIT", default=10, cast=int)

REDDIT_CLIENT_ID = config("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = config("REDDIT_CLIENT_SECRET", default="")
REDDIT_REFRESH_TOKEN = config("REDDIT_REFRESH_TOKEN")
USER_AGENT = config("REDDIT_USER_AGENT", default="newsfetcher by yourusername")


# --- Auth ---
def get_reddit_token_from_refresh():
    """Refresh the OAuth access token using the refresh token."""
    auth = requests.auth.HTTPBasicAuth(REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET)
    data = {
        "grant_type": "refresh_token",
        "refresh_token": REDDIT_REFRESH_TOKEN,
    }
    headers = {"User-Agent": USER_AGENT}

    try:
        response = requests.post(
            "https://www.reddit.com/api/v1/access_token",
            auth=auth,
            data=data,
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()
        return response.json().get("access_token")
    except requests.RequestException as e:
        print(f"[ERROR] Could not refresh Reddit token: {e}")
        return None


# --- Fetch ---
def fetch_reddit_posts(limit=10):
    """Fetch latest Reddit posts from a subreddit."""
    token = get_reddit_token_from_refresh()
    if not token:
        return []

    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": USER_AGENT,
    }

    url = f"{REDDIT_BASEURL}/r/{REDDIT_SUBREDDIT}/new?limit={limit}"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json().get("data", {}).get("children", [])
    except requests.RequestException as e:
        print(f"[ERROR] Could not fetch Reddit posts: {e}")
        return []


# --- Save to DB ---
def fetch_reddit_and_save(limit=10):
    """Fetch posts from Reddit and save them into RawNews."""
    posts = fetch_reddit_posts(limit)
    if not posts:
        print("[INFO] No posts fetched.")
        return

    source = fetch_or_create_source(
        name="Reddit",
        url="https://reddit.com",
        icon_url="https://www.redditstatic.com/desktop2x/img/favicon/favicon-32x32.png",
    )

    for post_data in posts:
        try:
            post = post_data.get("data", {})

            if not post.get("title"):
                continue

            RawNews.objects.update_or_create(
                source_news_id=post.get("id"),
                source=source,
                defaults={
                    "title": post.get("title", ""),
                    "description": post.get("selftext", "") or "",
                    "url": post.get("url")
                    or f"https://reddit.com{post.get('permalink', '')}",
                    "source_url": f"https://reddit.com{post.get('permalink', '')}",
                    "published_at": datetime.datetime.fromtimestamp(
                        post.get("created_utc", 0), tz=datetime.timezone.utc
                    ),
                    "fetched_at": datetime.datetime.now(datetime.timezone.utc),
                    "status": "raw",
                },
            )

        except IntegrityError as e:
            print(f"[DB ERROR] Failed to save post {post.get('id')}: {e}")
        except Exception as e:
            print(f"[ERROR] Unexpected error for post {post.get('id')}: {e}")
