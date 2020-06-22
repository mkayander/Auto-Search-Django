import json

from django.http import JsonResponse

from django.conf import settings
from django.shortcuts import render, redirect
from rest_framework.decorators import api_view

from .forms import FilterForm
from .models import CarElement, CarFilter, CarMark, CarModel, CityDB, RegionDB, Account, OtherFilter, OtherElement
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models.functions import Trunc
from django.utils import timezone
import pytz
from django.views.generic import ListView

from django.http import HttpResponseForbidden
from django.views.decorators.http import require_POST

from django.core.management import call_command
# from django.urls import reverse_lazy
from pytils.translit import slugify

import sys

from .MainClient import MainClient

sys.path.insert(1, 'main/client/')


@login_required
def index(request):
    return redirect('filter_list')


@login_required
def search(request, saved_filter=None):
    if saved_filter:
        filt = CarFilter.objects.filter(slug=saved_filter)
        if request.method == 'POST':
            data = request.POST.dict()
            print(data)
            del data['csrfmiddlewaretoken']
            del data['cityCount']

            cities_array = []

            for i in range(0, int(request.POST['cityCount'])):
                cities_array.append(request.POST[f'city{i}'])
                del data[f'city{i}']

            data['cities'] = '&'.join(cities_array)

            filt.update(**data)

            return redirect('filter_list')

        # filter_params = CarFilter.objects.get(slug=saved_filter)
        filter_params = list(filt.values())
    else:
        filter_params = ['']

    carMark = CarMark.objects.all().order_by('-isPopular').values('name')
    car_model = CarModel.objects.all().order_by('-isPopular').values('name', 'parentMark')
    city_db = CityDB.objects.all().order_by('-isPopular').values('name')
    region_db = RegionDB.objects.all().order_by('-isPopular').values('name')

    year_from_to = {'1960': '771', '1970': '782', '1980': '873', '1985': '878', '1990': '883', '1991': '884',
                    '1992': '885', '1993': '886', '1994': '887', '1995': '888',
                    '1996': '889', '1997': '890', '1998': '891', '1999': '892', '2000': '893', '2001': '894',
                    '2002': '895', '2003': '896', '2004': '897', '2005': '898',
                    '2006': '899', '2007': '900', '2008': '901', '2009': '902', '2010': '2844', '2011': '2845',
                    '2012': '6045', '2013': '8581', '2014': '11017',
                    '2015': '13978', '2016': '16381', '2017': '19775', '2018': '20303', '2019': '405242'}

    values_from_to = {'0,6': '15776', '0,8': '15778', '1,0': '15780', '1,2': '15782', '1,4': '15784', '1,6': '15786',
                      '1,8': '15788', '2,0': '15790', '2,2': '15792',
                      '2,4': '15794', '2,6': '15796', '2,8': '15798', '3,0': '15800', '3,5': '15805', '4,0': '15810',
                      '4,5': '15815', '5,0': '15820', '5,5': '15825',
                      '6,0': '15830'}

    settingsDict = {'city_db': city_db, 'region_db': region_db, 'carMark': carMark,
                    'car_model': car_model, 'year_from_to': year_from_to,
                    'value_from_to': values_from_to,
                    'filter_params': filter_params[0]
                    }

    return render(request, 'base.html', settingsDict)


@login_required
def otherSearch(request):
    cityDB = CityDB.objects.all().order_by('-isPopular').values('name')
    regionDB = RegionDB.objects.all().order_by('-isPopular').values('name')

    return render(request, 'otherSearch.html', {'cityDB': cityDB, 'regionDB': regionDB})


@login_required
def createFilter(request):
    with open('main/static/json/models.json') as jfile:
        carname_list = json.load(jfile)

    if request.method == 'POST':
        print(request.POST)
        form = FilterForm(request.POST)
        if form.is_valid():
            form.save()
            carname_mark = form.cleaned_data.get('carname_mark')
            messages.success(request, f'Фильтр для {carname_mark} успешно создан!')
            return redirect('index')
    else:
        form = FilterForm()
    print(form)
    return render(request, 'base.html', {'form': form, 'carname_list': carname_list})


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
        cities = CityDB.objects.all().values('name')
        regions = RegionDB.objects.all().values('name')
        for a in cities:
            if pop_cities == a['name']:
                pop_city = CityDB.objects.get(name=pop_cities)
                pop_city.popularCount += 1
                pop_city.save()
        for a in regions:
            if pop_cities == a['name']:
                pop_region = RegionDB.objects.get(name=pop_cities)
                pop_region.popularCount += 1
                pop_region.save()


def update_filter_data(fi, fi_c, filter_obj):
    """Обновление данных по существующему фильтру"""
    filter_config = {}

    if fi == 'cars':
        filter_config = {
            'type': 'car',
            'sites': ['avito', 'autoru'],
            'city': filter_obj.cities.split('&'),
            'carname': {'mark': filter_obj.carname_mark, 'model': filter_obj.carname_model},
            'hull': filter_obj.hull,
            'transm': filter_obj.transm,
            'fuel': filter_obj.fuel,
            'radius': str(filter_obj.radius),
            'price': [filter_obj.price_from or "", filter_obj.price_to or ""],
            'engine': [filter_obj.engine_from, filter_obj.engine_to],
            'year': [filter_obj.year_from or "", filter_obj.year_to or ""]
        }

    if fi == 'other':
        filter_config = {
            'type': 'other',
            'sites': ['avito', 'youla'],
            'city': filter_obj.cities.split('&'),
            'find': filter_obj.find.replace(' ', '+'),
            'radius': str(filter_obj.radius),
            'price': [filter_obj.price_from or "", filter_obj.price_to or ""],
        }

    client = MainClient()
    raw_results = client.requestCars(filter_config)

    response = {}

    if len(raw_results) > 0:
        old_cars_list = list(filter_obj.cars.values('e_id'))

        print(len(raw_results))
        filter_obj.quantity = len(raw_results)
        filter_obj.save()

        for old_car in old_cars_list:
            if old_car['e_id'] in raw_results:
                del raw_results[old_car['e_id']]

        car_list = raw_results.values()
        for car in car_list:
            car['parentFilter'] = filter_obj
            car['slug'] = slugify(f"{car['e_id']} {filter_obj.slug}")

        if car_list:
            print('Creating cars...')
            fi_c.objects.bulk_create([
                fi_c(**car) for car in car_list
            ])
            print('Cars are created!')
        else:
            print('No new cars found!')

        response = {
            'success': True,
            'code': 1,
            'new_cars': raw_results
        }
        print('Success on getting cars')

    else:
        response = {
            'success': False,
            'code': -1
        }
        print('Error on getting cars!')

    try:
        call_command('dbbackup', '0')
    except Exception as e:
        print(e)
    return response


@login_required
@require_POST
def result(request):
    fD = request.POST.dict()
    del fD['cityCount']
    # popUpdate(fD)
    cities_array = []

    for i in range(0, int(request.POST['cityCount'])):
        cities_array.append(request.POST[f'city{i}'])
        del fD[f'city{i}']

    fD['cities'] = '&'.join(cities_array)
    fD['owner'] = request.user
    fD['radius'] = int(fD['radius']) if fD['radius'] else 0
    fD['price_from'] = int(fD['price_from']) if fD['price_from'] else None
    fD['price_to'] = int(fD['price_to']) if fD['price_to'] else None
    fD['year_from'] = int(fD['year_from']) if fD['year_from'] else None
    fD['year_to'] = int(fD['year_to']) if fD['year_to'] else None

    # update_counters.send(sender=request.user.__class__, city="", carMark=fD['carname_mark'],
    # carModel=fD['carname_model'])

    filter_obj, filter_status = CarFilter.objects.get_or_create(**fD)
    print(filter_status)

    fi = "cars"
    fi_c = CarElement
    filter_updated = update_filter_data(fi, fi_c, filter_obj)

    if filter_updated['success']:
        # filter_obj.fid = fid
        # filter_obj.save()

        timezone.activate(pytz.timezone(settings.TIME_ZONE))
        settings_time_zone = pytz.timezone(settings.TIME_ZONE)
        db_arr = filter_obj.cars.all().values(
            'title',
            'archived',
            'created_at',
            'site',
            'year',
            'price',
            'url',
            'img',
            dtime_as_TZ=Trunc('created_at', 'second', tzinfo=settings_time_zone)
        ).order_by('price')

        print('---', f'Received {len(db_arr)} cars from DB', sep='\n')

        filter_object_dict = list(db_arr)

        json_response = {
            'success': True,
            'code': 1,
            'cars': filter_object_dict,
            'messages': [{
                'tag': 'info',
                'message': f'Успешно получено {len(db_arr)} результатов!'
            }]
        }
        if filter_updated['new_cars']:
            json_response['messages'].append({
                'tag': 'success',
                'message': f'Уникальных по данному запросу - {len(filter_updated["new_cars"])}'
            })
        print('Success on getting cars')

    else:
        json_response = {
            'success': True,
            'code': 1,
            'messages': [{
                'tag': 'danger',
                'message': 'Не удалось найти результаты по данному запросу.'}]
        }
        print('Error on getting cars!')

    return JsonResponse(json_response)


@login_required
@require_POST
def other_result(request):
    fD = request.POST.dict()
    del fD['cityCount']
    # popUpdate(fD)
    cities_array = []

    for i in range(0, int(request.POST['cityCount'])):
        cities_array.append(request.POST[f'city{i}'])
        del fD[f'city{i}']

    fD['cities'] = '&'.join(cities_array)
    fD['owner'] = request.user
    fD['radius'] = int(fD['radius']) if fD['radius'] else 0
    fD['price_from'] = int(fD['price_from']) if fD['price_from'] else None
    fD['price_to'] = int(fD['price_to']) if fD['price_to'] else None

    filter_obj, filter_status = OtherFilter.objects.get_or_create(**fD)
    print(filter_status)

    fi = "other"
    fi_c = OtherElement
    filter_updated = update_filter_data(fi, fi_c, filter_obj)

    if filter_updated['success']:
        # filter_obj.fid = fid
        # filter_obj.save()

        timezone.activate(pytz.timezone(settings.TIME_ZONE))
        settings_time_zone = pytz.timezone(settings.TIME_ZONE)
        db_arr = filter_obj.cars.all().values(
            'title',
            'archived',
            'created_at',
            'site',
            'price',
            'url',
            'img',
            dtime_as_TZ=Trunc('created_at', 'second', tzinfo=settings_time_zone)
        )

        print('---', f'Received {len(db_arr)} cars from DB', sep='\n')

        filter_object_dict = list(db_arr)

        json_response = {
            'success': True,
            'code': 1,
            'cars': filter_object_dict,
            'messages': [{
                'tag': 'info',
                'message': f'Успешно получено {len(db_arr)} результатов!'
            }]
        }
        if filter_updated['new_cars']:
            json_response['messages'].append({
                'tag': 'success',
                'message': f'Уникальных по данному запросу - {len(filter_updated["new_cars"])}'
            })
        print('Success on getting cars')

    else:
        json_response = {
            'success': True,
            'code': 1,
            'messages': [{
                'tag': 'danger',
                'message': 'Не удалось найти результаты по данному запросу.'}]
        }
        print('Error on getting cars!')

    return JsonResponse(json_response)


@login_required
def filterCarList(request):
    data = request.user.filters.values()
    # quantity = len(CarFilter.objects.all())

    return render(request, 'filters.html', {'data': list(data)})
    # return ListView.as_view(queryset=CarFilter.objects.filter(owner=request.user), template_name="filters.html")(request)


@login_required
def archiveAll(request):
    filt = CarFilter.objects.get(fid=request.POST['archive'])
    CarElement.objects.filter(parentFilter=filt).update(archived=True)
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
        db_arr = list(CarElement.objects.filter(parentFilter=filt, archived=True).order_by('-created_at'))
    else:
        db_arr = list(CarElement.objects.filter(parentFilter=filt, archived=False).order_by('-created_at'))

    return render(request, 'result.html', {'fid': filt.fid, 'db_arr': db_arr})


@login_required
def edit_filter(request):
    carMark = CarMark.objects.all().order_by('-isPopular').values('name')
    carModel = CarModel.objects.all().order_by('-isPopular').values('name', 'parentMark')
    cityDB = CityDB.objects.all().order_by('-isPopular').values('name')
    regionDB = RegionDB.objects.all().order_by('-isPopular').values('name')

    year_from_to = {'1960': '771', '1970': '782', '1980': '873', '1985': '878', '1990': '883', '1991': '884',
                    '1992': '885', '1993': '886', '1994': '887', '1995': '888',
                    '1996': '889', '1997': '890', '1998': '891', '1999': '892', '2000': '893', '2001': '894',
                    '2002': '895', '2003': '896', '2004': '897', '2005': '898',
                    '2006': '899', '2007': '900', '2008': '901', '2009': '902', '2010': '2844', '2011': '2845',
                    '2012': '6045', '2013': '8581', '2014': '11017',
                    '2015': '13978', '2016': '16381', '2017': '19775', '2018': '20303', '2019': '405242'}

    values_from_to = {'0,6': '15776', '0,8': '15778', '1,0': '15780', '1,2': '15782', '1,4': '15784', '1,6': '15786',
                      '1,8': '15788', '2,0': '15790', '2,2': '15792',
                      '2,4': '15794', '2,6': '15796', '2,8': '15798', '3,0': '15800', '3,5': '15805', '4,0': '15810',
                      '4,5': '15815', '5,0': '15820', '5,5': '15825',
                      '6,0': '15830'}

    settings_dict = {'cityDB': cityDB, 'regionDB': regionDB, 'carMark': carMark,
                     'carModel': carModel, 'year_from_to': year_from_to,
                     'value_from_to': values_from_to}

    return render(request, 'base.html', settings_dict)


@login_required
def filter_form(request):
    if request.method == 'POST':
        print(request.POST)
        form = FilterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = FilterForm()
    return render(request, 'baseForm.html', {'form': form})
