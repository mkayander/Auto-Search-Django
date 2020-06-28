from django_cron import CronJobBase, Schedule
from .models import CarFilter, CarElement
from .views import update_filter_data

class UpdateFiltersCron(CronJobBase):
    RUN_EVERY_MINS = 2
    #MIN_NUM_FAILURES = 3

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'main.update_filter'    # a unique code

    def do(self):
        for f in CarFilter.objects.all():
            update_filter_data(f)