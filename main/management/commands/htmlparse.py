import json

from bs4 import BeautifulSoup
from colorama import Fore
from django.core.management.base import BaseCommand
from pytils.translit import slugify

from main.models import CarMark, CarModel


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("action", nargs='+', type=str)

    def handle(self, *args, **options):
        if "parse-models" in options["action"]:
            with open("main/management/html_doc.html", 'r', encoding="utf-8") as html_doc:
                soup = BeautifulSoup(html_doc, "html.parser")
                result = []
                for model in soup.select(".popular-rubricator-row-2oc-J"):
                    title = model.a["title"]
                    result.append({
                        "title": title,
                        "slug": slugify(title)
                    })

                print(result)
                print(Fore.GREEN + "Success")

                with open("main/management/models_result.json", 'w+', encoding="utf-8") as outfile:
                    json.dump(result, outfile, sort_keys=True, indent=4)

        if "load" in options["action"]:
            with open("main/management/models_result.json", 'r', encoding="utf-8") as file:
                model_names = json.load(file)
                mark = CarMark.objects.get(avito="vaz_lada")
                for model in model_names:
                    CarModel.objects.create(
                        name=model["title"],
                        mark=mark,
                        avito=model["slug"],
                        autoru=model["slug"],
                        drom=model["slug"],
                        youla=model["slug"])

                print(Fore.GREEN + "Success")
