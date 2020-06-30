from django.db import models
from pytils.translit import slugify

from account.models import Account


class AbstractOptionModel(models.Model):
    isPopular = models.BooleanField(default=False)
    popularCount = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True


class AbstractElementModel(models.Model):
    e_id = models.CharField(max_length=100, primary_key=True)
    archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    site = models.CharField(max_length=10)
    title = models.CharField(max_length=200)
    city = models.CharField(max_length=50, blank=True)
    price = models.PositiveIntegerField(blank=True, null=True)
    url = models.URLField(max_length=300, db_index=True, blank=True)
    img = models.URLField(max_length=300, db_index=True, blank=True)

    class Meta:
        abstract = True
        ordering = ['price']


class AbstractBaseFilterModel(models.Model):
    owner = models.ForeignKey(Account, related_name="", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0, verbose_name="Результатов", help_text="По данному фильтру")
    radius = models.PositiveSmallIntegerField(verbose_name="Радиус поиска", help_text="В километрах", blank=True,
                                              default=0)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    price_from = models.PositiveIntegerField(verbose_name="Цена От", blank=True, null=True)
    price_to = models.PositiveIntegerField(verbose_name="Цена До", blank=True, null=True)
    refresh_count = models.PositiveIntegerField(default=0, verbose_name="Количество обновлений",
                                                help_text="Сколько раз была обновлена информация по фильтру")

    class Meta:
        abstract = True
        ordering = ['created_at']


class AbstractLocationModel(models.Model):
    avito = models.CharField(max_length=60)
    autoru = models.CharField(max_length=60)
    drom = models.CharField(max_length=60)
    youla = models.CharField(max_length=60)
    popularCount = models.PositiveIntegerField(default=1)
    isPopular = models.BooleanField(default=False)

    def __str__(self):
        return self.avito

    class Meta:
        abstract = True
        ordering = ['avito']


# ---------------------------------------------------------------------------------------


class RegionDB(AbstractLocationModel):
    name = models.CharField(max_length=60, primary_key=True)


class CityDB(AbstractLocationModel):
    name = models.CharField(max_length=60)
    region = models.ForeignKey(RegionDB, related_name='cities', on_delete=models.CASCADE, null=True)


class CarMark(AbstractOptionModel):
    name = models.CharField(max_length=60, primary_key=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class CarModel(AbstractOptionModel):
    name = models.CharField(max_length=60)
    mark = models.ForeignKey(CarMark, related_name='models', on_delete=models.CASCADE)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.mark.name} {self.name}'


class CarFilter(AbstractBaseFilterModel):
    owner = models.ForeignKey(Account, related_name='filters', on_delete=models.CASCADE)
    regions = models.ManyToManyField('RegionDB', related_name="filters")
    cities = models.ManyToManyField('CityDB', related_name="filters")
    car_marks = models.ManyToManyField(CarMark, related_name="filters")
    car_models = models.ManyToManyField(CarModel, related_name="filters")
    hull = models.CharField(max_length=20, verbose_name="Кузов", blank=True)
    fuel = models.CharField(max_length=20, verbose_name="Тип двигателя", blank=True)
    transmission = models.CharField(max_length=20, verbose_name="Трансмиссия", blank=True)
    year_from = models.PositiveSmallIntegerField(verbose_name="Год выпуска От", blank=True, null=True)
    year_to = models.PositiveSmallIntegerField(verbose_name="Год выпуска До", blank=True, null=True)
    engine_from = models.CharField(max_length=4, verbose_name="Объём двигателя От", blank=True)
    engine_to = models.CharField(max_length=4, verbose_name="Объём двигателя До", blank=True)

    def __str__(self):
        # TODO: If this dynamic string-slug is OK, write it to field upon save, read value in this function
        marks_names = models_names = city_names = region_names = ""
        for s in self.car_marks.values("name"): marks_names += s['name'] + " "
        for s in self.car_models.values("name"): models_names += s['name'] + " "
        for s in self.regions.values("name"): city_names += s['name'] + " "
        for s in self.cities.values("name"): region_names += s['name'] + " "
        return f'{self.owner.username} {marks_names}{models_names}{city_names}{region_names}'


class CarElement(AbstractElementModel):
    """Модель результата поиска - автомобиль"""
    year = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return f'{self.e_id} {self.pk}'


class OtherFilter(AbstractBaseFilterModel):
    find = models.CharField(max_length=100)
    owner = models.ForeignKey(Account, related_name='other_filters', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.owner} {self.find}'


class OtherElement(AbstractElementModel):

    def __str__(self):
        return f'{self.e_id} {self.pk}'
