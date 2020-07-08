import asyncio
import json

from aiofile import AIOFile
from django.apps import apps
from django.core.management.base import BaseCommand
from pytils.translit import slugify

from main.models import RegionDB, CityDB, CarMark, CarModel


async def write_json(data):
    async with AIOFile('main/management/db.json', 'w+') as file:
        await file.write(json.dumps(data, sort_keys=True, indent=4))
        await file.fsync()


async def read_json():
    async with AIOFile('main/management/db.json', 'r') as file:
        raw_init_filter = await file.read()
        return json.loads(raw_init_filter)


class Command(BaseCommand):
    help = "Choose the command: reload , restore , or any value to backup DB to file"

    def add_arguments(self, parser):
        parser.add_argument('load', nargs='+', type=str)

    def handle(self, *args, **options):
        print(options['load'])
        if 'reload' in options['load']:
            saved_data = asyncio.run(read_json())
            for key, values in saved_data.items():
                print(*['----------', f'Reloading -- {key}'], sep='\n')
                model = apps.get_model("main", key)
                for obj in values:
                    if model.objects.filter(**obj).exists():
                        m = model.objects.get(**obj)
                        m.save()
                    else:
                        print(f'Not found -- {obj}')

        elif 'restore' in options['load']:
            saved_data = asyncio.run(read_json())
            for key, values in saved_data.items():
                model = apps.get_model("main", key)
                for obj in values:
                    try:
                        db_entry = model.objects.get(slug=obj['slug'])
                    except model.DoesNotExist:
                        print(f'Restoring -- {obj}')
                        model.objects.create(**obj)

            print("SUCCESS!")

        elif 'load-marks' in options['load']:
            saved_data = asyncio.run(read_json())
            for obj in saved_data["CarMark"]:
                model = apps.get_model("main", "CarMark")
                # try:
                #     model.objects.get(name=obj['slug'])
                # except model.DoesNotExist:
                print(f'Restoring -- {obj}')
                model.objects.create(**obj)

        elif 'load-models' in options['load']:
            saved_data = asyncio.run(read_json())
            for obj in saved_data["CarModel"]:
                model = apps.get_model("main", "CarModel")
                # try:
                #     model.objects.get(name=obj['slug'])
                # except model.DoesNotExist:
                obj["mark"] = CarMark.objects.get(slug=obj["mark_id"])
                del obj["mark_id"]
                print(f'Restoring -- {obj}')
                model.objects.create(**obj)

        elif 'load-cities' in options['load']:
            saved_data = asyncio.run(read_json())
            for obj in saved_data["CityDB"]:
                model = apps.get_model("main", "CityDB")
                # try:
                #     model.objects.get(name=obj['slug'])
                # except model.DoesNotExist:
                obj["region"] = RegionDB.objects.get(slug=obj["region_id"])
                del obj["region_id"]
                print(f'Restoring -- {obj}')
                model.objects.create(**obj)

        else:
            db = {
                'CityDB': list(CityDB.objects.values()),
                'RegionDB': list(RegionDB.objects.values()),
                'CarMark': list(CarMark.objects.values()),
                'CarModel': list(CarModel.objects.values())
            }
            asyncio.run(write_json(db))
            print('Backed Up to db.json')
