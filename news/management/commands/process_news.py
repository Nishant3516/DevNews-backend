from django.core.management.base import BaseCommand
from news.tagger.tag_news import process_raw_news


class Command(BaseCommand):
    help = "Processes raw news into tagged and categorized news."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Processing raw news..."))
        process_raw_news()
        self.stdout.write(self.style.SUCCESS("News processing complete."))
