from django.apps import apps
from django.core.management.base import BaseCommand
from main.models import SearchTargetModel
from colorama import Fore


class Command(BaseCommand):
    help = """Handy tool to manage all instances of models that inherit SearchTargetModel"""

    def add_arguments(self, parser):
        parser.add_argument("action", nargs='+', type=str)

    def handle(self, *args, **options):
        print(options)
        if options["action"]:
            for model in apps.get_app_config("main").get_models():
                if issubclass(model, SearchTargetModel):
                    print(Fore.LIGHTCYAN_EX + str(model))
                    for obj in model.objects.iterator():

                        if "fill" in options["action"]:
                            obj.avito = obj.name if not obj.avito and obj.name else obj.avito
                            obj.autoru = obj.avito if not obj.autoru else obj.autoru
                            obj.drom = obj.avito if not obj.drom else obj.drom
                            obj.youla = obj.avito if not obj.youla else obj.youla

                        if "to-lower" in options["action"]:
                            obj.avito = obj.avito.lower()
                            obj.autoru = obj.autoru.lower()
                            obj.drom = obj.drom.lower()
                            obj.youla = obj.youla.lower()

                        obj.save()

        print(Fore.GREEN + "Success!")
