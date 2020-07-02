import django.dispatch

update_counters = django.dispatch.Signal(providing_args=["city", "carMark", "carModel"])


