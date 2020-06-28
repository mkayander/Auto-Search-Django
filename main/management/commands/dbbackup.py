import asyncio
import json

from aiofile import AIOFile
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
                model = globals()[key]
                for obj in values:
                    if model.objects.filter(**obj).exists():
                        m = model.objects.get(**obj)
                        m.save()
                    else:
                        print(f'Not found -- {obj}')

        elif 'restore' in options['load']:
            saved_data = asyncio.run(read_json())
            for key, values in saved_data.items():
                model = globals()[key]
                for obj in values:
                    try:
                        db_entry = model.objects.get(slug=obj['slug'])
                    except model.DoesNotExist:
                        print(f'Restoring -- {obj}')
                        model.objects.create(**obj)

            print("SUCCESS!")

        elif 'carmark-key-slugify' in options['load']:
            mutable_data = asyncio.run(read_json())
            for carmark in mutable_data['CarModel']:
                # print(carmark)
                print(carmark, carmark['parentMark_id'])
                carmark['parentMark_id'] = slugify(carmark['parentMark_id'])

            asyncio.run(write_json(mutable_data))

        elif 'citydb-region-slugify' in options['load']:
            mutable_data = asyncio.run(read_json())
            for city in mutable_data['CityDB']:
                city['region_id'] = slugify(city['region_id'])
                print(city, city['region_id'])

            asyncio.run(write_json(mutable_data))

        else:
            db = {
                'CityDB': list(CityDB.objects.values()),
                'RegionDB': list(RegionDB.objects.values()),
                'CarMark': list(CarMark.objects.values()),
                'CarModel': list(CarModel.objects.values())
            }
            asyncio.run(write_json(db))
            print('Backed Up to db.json')
