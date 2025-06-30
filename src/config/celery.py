import os
from celery import Celery
from celery.schedules import crontab
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'tuesday-noon-task': {
        'task': 'wms.tasks.tuesday_noon_task',
        'schedule': crontab(hour=12, minute=0, day_of_week=2),
    },
    'birthday-task': {
        'task': 'wms.tasks.birthday_task',
        'schedule': crontab(minute=0, hour=12, day_of_month=2, month_of_year=9),
    },
    'leap-friday-13-task': {
        'task': 'wms.tasks.leap_friday_13_task',
        'schedule': crontab(minute=13, day_of_week=5, day_of_month=13),
    },
}