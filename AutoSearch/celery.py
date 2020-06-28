import os
from celery import Celery
from celery.schedules import crontab
 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AutoSearch.settings')
 
app = Celery('AutoSearch')
app.config_from_object('django.conf:settings')
 
# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send-report-every-single-minute': {
        'task': 'main.tasks.auto_filter',
        'schedule': crontab(minute='*/2'),  # change to `crontab(minute=0, hour=0)` if you want it to run daily at midnight
    },
}