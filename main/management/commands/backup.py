import json

from django.apps import apps
from django.core.management.base import BaseCommand
from django.core.serializers.json import DjangoJSONEncoder

from main.models import Region


def get_item_key(obj):
    return obj["id"] if "id" in obj else obj["name"]


class Command(BaseCommand):
    help = "Gets all needed data from Django database, converts it to JSON and stores on disk"

    def add_arguments(self, parser):
        parser.add_argument('action', nargs='+', type=str)

    def handle(self, *args, **options):
        if "all" in options["action"]:
            db = []
            for model in apps.get_app_config("main").get_models():
                db.append((model.__name__, list(model.objects.values())))

            with open("db.json", 'w+') as outfile:
                json.dump(db, outfile, sort_keys=True, indent=4, cls=DjangoJSONEncoder)
            self.stdout.write(self.style.SUCCESS("Successfully backed up database to db.json"))

        elif "restore" in options["action"]:
            with open("db.json", 'r') as file:
                models_array = json.load(file)
                for name, data in models_array:
                    model = apps.get_model("main", name)
                    for obj in data:
                        try:
                            model.objects.get(pk=get_item_key(obj))
                        except model.DoesNotExist:
                            print(f'Restoring -- {obj}')
                            model.objects.create(**obj)

                self.stdout.write(self.style.SUCCESS("Successfully restored database from db.json"))

        elif "manual" in options["action"]:
            with open("db.json", 'r') as file:
                models_array = json.load(file)
                for obj in models_array["CityDB"]:
                    model = apps.get_model("main", "CityDB")
                    # try:
                    #     model.objects.get(name=obj['slug'])
                    # except model.DoesNotExist:
                    obj["region"] = Region.objects.get(name=obj["region_id"])
                    del obj["region_id"]
                    print(f'Restoring -- {obj}')
                    model.objects.create(**obj)

        elif "reload-all" in options["action"]:
            with open("db.json", 'r') as file:
                models_array = json.load(file)
                for name, data in models_array.items():
                    model = apps.get_model("main", name)
                    for obj in data:
                        try:
                            instance = model.objects.get(pk=get_item_key(obj))

                            for attr, value in obj.items():
                                setattr(instance, attr, value)
                            instance.save()
                        except model.DoesNotExist:
                            self.stdout.write(self.style.ERROR(f"Object {obj} does not exist!"))

                self.stdout.write(self.style.SUCCESS("Reloaded from db.json"))

        else:
            self.stdout.write(self.style.ERROR(f"Action {options['action']} not recognized!"))
