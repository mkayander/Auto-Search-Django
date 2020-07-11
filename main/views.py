import sys

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect

from .models import CarResult, CarFilter

sys.path.insert(1, 'main/client/')


@login_required
def index(request):
    return redirect('filter_list')


@login_required
def filter_car_list(request):
    data = request.user.filters.values()
    # quantity = len(CarFilter.objects.all())

    return render(request, 'filters.html', {'data': list(data)})


@login_required
def saved(request, slug, archived=''):
    filt = CarFilter.objects.get(slug=slug)
    if not filt.owner == request.user:
        return HttpResponseForbidden()

    if archived == 'archived':
        db_arr = list(CarResult.objects.filter(parentFilter=filt, archived=True).order_by('-created_at'))
    else:
        db_arr = list(CarResult.objects.filter(parentFilter=filt, archived=False).order_by('-created_at'))

    return render(request, 'result.html', {'fid': filt.fid, 'db_arr': db_arr})
