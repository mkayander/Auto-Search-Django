from django.db import models

from account.models import Account


# --- Abstract Base Models --------------------------------------------------------------

class StatisticsModel(models.Model):
    """Abstract model. Mainly designed for option models, to track their usage count."""
    is_popular = models.BooleanField(verbose_name="Является популярным", default=False)
    request_count = models.PositiveIntegerField(verbose_name="Кол-во использований", default=0)

    class Meta:
        abstract = True


class ResultModel(models.Model):
    """
    Abstract model. Describes a common product with properties that are present on any product marketplace website.
    This can be a base for the car, furniture or any other product search result.
    """
    e_id = models.CharField(verbose_name="Внешний id", help_text="Уникальный ключ продукта на стороннем веб-сайте",
                            max_length=100, primary_key=True)
    archived = models.BooleanField(verbose_name="Результат заархивирован", default=False)
    created_at = models.DateTimeField(verbose_name="Дата записи", auto_now_add=True, editable=True)
    site = models.CharField(verbose_name="Веб-сайт", help_text="Сайт, на котором был найден продукт", max_length=10)
    title = models.CharField(verbose_name="Наименование", max_length=200)
    city = models.CharField(verbose_name="Город", help_text="Локация продукта", max_length=50, blank=True)
    price = models.PositiveIntegerField(verbose_name="Стоимость", blank=True, null=True)
    url = models.URLField(verbose_name="Ссылка", help_text="Ссылка на сайт с данным продуктом", max_length=300,
                          db_index=True, blank=True)
    img = models.URLField(verbose_name="Ссылка на фото", max_length=300, db_index=True, blank=True)

    class Meta:
        abstract = True
        ordering = ['created_at']


class BaseFilterModel(models.Model):
    """
    Abstract model. Common search filter properties for various types of the product.
    """
    owner = models.ForeignKey(Account, verbose_name="Автор фильтра", related_name="filters", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name="Результатов", default=0, help_text="По данному фильтру")
    radius = models.PositiveSmallIntegerField(verbose_name="Радиус поиска", help_text="В километрах", blank=True,
                                              default=0)
    created_at = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True, editable=True)
    price_from = models.PositiveIntegerField(verbose_name="Цена От", blank=True, null=True)
    price_to = models.PositiveIntegerField(verbose_name="Цена До", blank=True, null=True)
    refresh_count = models.PositiveIntegerField(verbose_name="Количество обновлений", default=0,
                                                help_text="Сколько раз была обновлена информация по фильтру")

    class Meta:
        abstract = True
        ordering = ['created_at']


class SearchTargetModel(models.Model):
    """
    Abstract class. Describes search slug fields for supported websites.
    These values are meant to be used when constructing a URL string with needed options/queries.
    """
    avito = models.CharField(verbose_name="avito.ru slug", max_length=60, blank=True)
    autoru = models.CharField(verbose_name="auto.ru slug", max_length=60, blank=True)
    drom = models.CharField(verbose_name="drom.ru slug", max_length=60, blank=True)
    youla = models.CharField(verbose_name="youla.ru slug", max_length=60, blank=True)

    class Meta:
        abstract = True


# ---------------------------------------------------------------------------------------


class Region(SearchTargetModel):
    """Geographic region that contain cities. Inherits search slugs."""
    name = models.CharField(verbose_name="Наименование", max_length=60)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class City(SearchTargetModel):
    """Geographic city that relate to it's region."""
    name = models.CharField(verbose_name="Наименование", max_length=60)
    region = models.ForeignKey(Region, verbose_name="Регион", help_text="Регион, в которых входит город",
                               related_name='cities', on_delete=models.CASCADE, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class CarMark(SearchTargetModel):
    """Mark/manufacturer of the car, like BMW, Audi etc."""
    name = models.CharField(verbose_name="Наименование", max_length=60)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class CarModel(SearchTargetModel):
    """Model of the car that relates to a certain mark/manufacturer."""
    name = models.CharField(verbose_name="Наименование", max_length=60)
    mark = models.ForeignKey(CarMark, verbose_name="Марка/Производитель", related_name='models',
                             on_delete=models.CASCADE)

    class Meta:
        ordering = ['mark', 'name']

    def __str__(self):
        return f'{self.mark.name} {self.name}'


class CarResult(ResultModel):
    """Search result that is a car."""
    year = models.PositiveIntegerField(verbose_name="Год производства авто", blank=True, null=True)

    def __str__(self):
        return f'{self.e_id} {self.pk}'


class CarFilter(BaseFilterModel):
    """Search filter that extends base product filter and has properties/options to search a car."""
    owner = models.ForeignKey(Account, verbose_name="Автор фильтра", related_name="filters", on_delete=models.CASCADE)
    cars = models.ManyToManyField(CarResult, verbose_name="Автомобили", related_name="filters")
    regions = models.ManyToManyField("main.Region", verbose_name="Регионы поиска", related_name="filters")
    cities = models.ManyToManyField("main.City", verbose_name="Города поиска", related_name="filters")
    car_marks = models.ManyToManyField(CarMark, verbose_name="Марки авто", related_name="filters")
    car_models = models.ManyToManyField(CarModel, verbose_name="Модели авто", related_name="filters")
    hull = models.CharField(verbose_name="Кузов", max_length=20, blank=True)
    fuel = models.CharField(verbose_name="Тип двигателя", max_length=20, blank=True)
    transmission = models.CharField(verbose_name="Трансмиссия", max_length=20, blank=True)
    year_from = models.PositiveSmallIntegerField(verbose_name="Год выпуска От", blank=True, null=True)
    year_to = models.PositiveSmallIntegerField(verbose_name="Год выпуска До", blank=True, null=True)
    engine_from = models.CharField(verbose_name="Объём двигателя От", max_length=4, blank=True)
    engine_to = models.CharField(verbose_name="Объём двигателя До", max_length=4, blank=True)

    def __str__(self):
        # TODO: If this dynamic string-slug is OK, write it to field upon save, read value in this function
        marks_names = models_names = city_names = region_names = ""
        for s in self.car_marks.values("name"): marks_names += s['name'] + " "
        for s in self.car_models.values("name"): models_names += s['name'] + " "
        for s in self.regions.values("name"): city_names += s['name'] + " "
        for s in self.cities.values("name"): region_names += s['name'] + " "
        return f'{self.owner.username} {marks_names}{models_names}{city_names}{region_names}'


class OtherFilter(BaseFilterModel):
    """Search filter that extends base product filter. Generic search based on a string query."""
    find = models.CharField(max_length=100)
    owner = models.ForeignKey(Account, related_name='other_filters', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.owner} {self.find}'


class OtherResult(ResultModel):
    """Generic search result based in the string query of the OtherFilter."""

    def __str__(self):
        return f'{self.e_id} {self.pk}'
