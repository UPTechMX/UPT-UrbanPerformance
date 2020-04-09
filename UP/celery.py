from __future__ import absolute_import, unicode_literals
import os
import sqlalchemy
from celery import Celery
from django.db import connection as db
from decouple import config

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UP.settings')
app = Celery('UP')


broker ="sqla+postgres://" + config('DB_USER') + ":" + config('DB_PASSWORD') + "@" + config('DB_HOST') + ":" + config('DB_PORT') + "/" + config('DB_NAME')

app.config_from_object('django.conf:settings', namespace='CELERY') 
app.autodiscover_tasks()  
app.conf.update(BROKER_URL=broker, worker_max_tasks_per_child=1, )
@app.task(bind=True)
def debug_task(self):
    print('Request: {0}'.format(self.request))