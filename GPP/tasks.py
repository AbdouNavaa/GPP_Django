from celery import shared_task
from .views import create_courses_for_day
from datetime import datetime

@shared_task
def generate_courses_task():
    print('dfdsf')
    day_name = datetime.now().strftime('%A')  # Obtenir le nom du jour actuel
    daysOfWeek = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    create_courses_for_day(daysOfWeek[day_name])
