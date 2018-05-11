from __future__ import absolute_import
from celery import Celery
from kombu import Queue, Exchange

app = Celery(
    'tasks', 
    broker='pyamqp://admin:admin@172.16.0.2',
    backend="rpc://"
)
app.conf.task_queues = (
    Queue('default', Exchange('default'), routing_key='default'),
    Queue('parsing',  Exchange('parsing'),   routing_key='parsing'),
    Queue('download',  Exchange('download'),   routing_key='download'),
)