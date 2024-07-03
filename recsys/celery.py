import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recsys.settings')
app = Celery('recsys', broker='pyamqp://guest@localhost//')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
app.conf.beat_schedule = {
    'test_task': {
        'task': 'reviewmaster.tasks.test',
        'schedule': crontab(minute='*')#every minute
    },
    'daily_training_task': {
        'task': 'reviewmaster.tasks.train_model',
        'schedule': crontab(hour=0)#every day
    }
}