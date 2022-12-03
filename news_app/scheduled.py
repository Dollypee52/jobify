
from django.core.management.base import BaseCommand
from news_app.utils import scheduled_tasks1


class Command(BaseCommand):
    help = "Scheduled data fetching from hackernews for every 5 minutes"

    def handle(self, *args, **options):
        scheduled_tasks1()