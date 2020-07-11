import json

from bs4 import BeautifulSoup
from colorama import Fore
from django.core.management.base import BaseCommand
from pytils.translit import slugify


class Command(BaseCommand):
    def handle(self, *args, **options):
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

            with open("main/management/models_result.json", 'w+', encoding="utf-8") as outfile:
                json.dump(result, outfile, sort_keys=True, indent=4)
