import models

'''
To run scheduler

./manage.py shell
from django_q.models import Schedule
Schedule.objects.create(
    func='salesrepr.tasks.set_counter_daily',
    schedule_type=Schedule.DAILY,
    repeats=-1
)
./manage.py qcluster
'''
def set_counter_daily():
    models.counter=0
    