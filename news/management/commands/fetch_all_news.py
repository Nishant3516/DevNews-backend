from django.core.management.base import BaseCommand
from news.fetchers import hackernews_fetcher, reddit_fetcher, dev_to_fetcher, techcrunch_fetcher


class Command(BaseCommand):
    help = "Fetch news from all sources and process them"

    def handle(self, *args, **kwargs):
        dev_to_fetcher.fetch_devto()
        # reddit_fetcher.fetch_reddit_and_save()
        # hackernews_fetcher.fetch_hackernews()
        techcrunch_fetcher.fetch_techcrunch()
