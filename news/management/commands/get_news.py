from django.core.management.base import BaseCommand
from django.core.management import call_command
import logging

logger = logging.getLogger('cron')


class Command(BaseCommand):
    help = "Fetch news first, then process them"

    def handle(self, *args, **kwargs):
        try:
            logger.info("Cron job started")
            call_command("fetch_all_news")
            logger.info("News Fetched successfully")
            call_command('process_news')
            logger.info("News Processed successfully")
        except Exception as e:
            logger.error("Something went wrong: %s", e, exc_info=True)
