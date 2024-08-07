from django.core.management.base import BaseCommand
from .models import *
from datetime import datetime

class Command(BaseCommand):
    help = 'Generate courses for today'

    def handle(self, *args, **kwargs):
        day_name = datetime.now().strftime("%A")
        create_courses_for_day(day_name)
        self.stdout.write(self.style.SUCCESS('Successfully created courses for today'))
