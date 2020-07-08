import sys

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect

from .models import CarResult, CarFilter, CarMark, CarModel, City, Region

sys.path.insert(1, 'main/client/')


@login_required
def index(request):
    return redirect('filter_list')


def pop_update(filter_data):
    mark = filter_data['carname_mark']
    model = filter_data['carname_model']
    pop_cities = filter_data['city0']
    print(pop_cities)

    if not mark == '':
        pop_mark = CarMark.objects.get(name=mark)
        pop_mark.popularCount += 1
        pop_mark.save()

    if not model == '':
        pop_model = CarModel.objects.get(name=model)
        pop_model.popularCount += 1
        pop_model.save()

    if not pop_cities == '':
        cities = City.objects.all().values('name')
        regions = Region.objects.all().values('name')
        for a in cities:
            if pop_cities == a['name']:
                pop_city = City.objects.get(name=pop_cities)
                pop_city.popularCount += 1
                pop_city.save()
        for a in regions:
            if pop_cities == a['name']:
                pop_region = Region.objects.get(name=pop_cities)
                pop_region.popularCount += 1
                pop_region.save()


@login_required
def filter_car_list(request):
    data = request.user.filters.values()
    # quantity = len(CarFilter.objects.all())

    return render(request, 'filters.html', {'data': list(data)})


@login_required
def archiveAll(request):
    filt = CarFilter.objects.get(fid=request.POST['archive'])
    CarResult.objects.filter(parentFilter=filt).update(archived=True)
    # for a in db_arch:
    #     if a.archived == False:
    #         a.archived = True

    # for a in db_arch:
    #     print(a.archived)

    return saved(request, filt.id, archived='archived')


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
