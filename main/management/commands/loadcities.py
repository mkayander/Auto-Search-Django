import json

import transliterate
from main.models import Region, City
from django.core.management.base import BaseCommand

with open("static/json/russia1.json") as file:
    russiaList = json.load(file)


class Command(BaseCommand):
    help = "Whatever you want to print here"

    def handle(self, *args, **options):
        for a in russiaList:
            d = transliterate.translit(a['city'], reversed=True).lower().replace(' ', '_').strip("'")
            tmp = City(city=a['city'],
                       region=Region.objects.get(region=a['region']),
                       avitoCity=d,
                       autoruCity=d,
                       dromCity=d,
                       youlaCity=d,
                       popularCount=1)
            tmp.save()
            print(tmp)
        # for a in russiaList:
        #     tmp.update({a['region'] : True})
        # # print(tmp.keys())

        # for r in tmp.keys():
        #     d = transliterate.translit(r, reversed=True).lower().replace(' ', '_')
