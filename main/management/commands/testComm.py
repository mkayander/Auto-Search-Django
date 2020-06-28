from django.core.management.base import BaseCommand, CommandError
from AioTest.models import CarMark, CarModel
import json

with open("AioTest/static/json/models.json") as jfile:
    modelsDict = json.load(jfile)

class Command(BaseCommand):

    help = "Whatever you want to print here"

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_ids', nargs='+', type=int)

    def handle(self, *args, **options):
        for a, b in modelsDict.items():
            c = CarMark(name=a, popularCount=1)
            c.save()
            print(str(c))
            for d in b:
                if not d == '':
                    l = CarModel(name=d, parentMark=c, popularCount=1)
                    l.save()
                    print(str(l))
                else:
                    print('empty model skipped')