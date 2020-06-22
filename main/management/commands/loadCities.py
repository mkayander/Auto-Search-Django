from django.core.management.base import BaseCommand, CommandError
from WebInt.main.models import RegionDB, CityDB
import json
import transliterate

with open("AioTest/static/json/russia1.json") as jfile:
    russiaList = json.load(jfile)


class Command(BaseCommand):

    help = "Whatever you want to print here"

    def handle(self, *args, **options):
        
        for a in russiaList:
            d = transliterate.translit(a['city'], reversed=True).lower().replace(' ', '_').strip("'")
            tmp = CityDB(city=a['city'], 
                        region=RegionDB.objects.get(region=a['region']),
                        avitoCity=d,
                        autoruCity=d,
                        dromCity=d,
                        youlaCity=d,
                        popularCount=1 )
            tmp.save()
            print(tmp)
        # for a in russiaList:
        #     tmp.update({a['region'] : True})
        # # print(tmp.keys())

        # for r in tmp.keys():
        #     d = transliterate.translit(r, reversed=True).lower().replace(' ', '_')
            

                