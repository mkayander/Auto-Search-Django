from .views import update_filter_data
from .models import CarFilter
from AutoSearch.celery import app


@app.task
def auto_filter():
    for f in CarFilter.objects.all():
        update_filter_data(f)
