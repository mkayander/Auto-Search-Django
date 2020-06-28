from django.db import models
from django.utils.crypto import get_random_string
from pytils.translit import slugify

from account.models import Account


# class BaseModel(models.Model, metaclass=ABCMeta):
#
#     @abstractmethod
#     def get_slug(self):
#         pass
#
#     def __str__(self):
#         return self.get_slug()
#
#     class Meta:
#         abstract = True


class AbstractOptionModel(models.Model):
    slug = models.SlugField(unique=True, primary_key=True)
    # name = models.CharField(max_length=60, unique=True, primary_key=True)
    isPopular = models.BooleanField(default=False)
    popularCount = models.PositiveIntegerField(default=0)

    def get_slug(self):
        new_slug = slugify(str(self))
        qs = self.__class__.objects.filter(slug=new_slug).exclude(pk=self.pk)
        if qs.exists():
            alt_field = str(self.__class__._meta.get_fields()[4].value_from_object(self))
            slug = slugify(new_slug + ' ' + alt_field)
            print(f'Altering slug! -- {slug}! pk: {self.pk}')
            return slug

        return new_slug

    class Meta:
        abstract = True
        ordering = ['slug']


class AbstractElementModel(models.Model):
    slug = models.SlugField(blank=True, null=True, unique=True)
    e_id = models.CharField(max_length=100)
    archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    site = models.CharField(max_length=10)
    title = models.CharField(max_length=200)
    city = models.CharField(max_length=50, blank=True)
    price = models.PositiveIntegerField(blank=True, null=True)
    url = models.URLField(max_length=300, db_index=True, blank=True)
    img = models.URLField(max_length=300, db_index=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(str(self))
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
        ordering = ['price']


class AbstractBaseFilterModel(models.Model):
    initialized = models.BooleanField(default=False)
    slug = models.SlugField(blank=True, null=True, unique=True, help_text="Идентификатор")
    owner = models.ForeignKey(Account, related_name="", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0, verbose_name="Результатов", help_text="По данному фильтру")
    radius = models.PositiveSmallIntegerField(verbose_name="Радиус поиска", help_text="В километрах", blank=True,
                                              default=0)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    price_from = models.PositiveIntegerField(verbose_name="Цена От", blank=True, null=True)
    price_to = models.PositiveIntegerField(verbose_name="Цена До", blank=True, null=True)
    refresh_count = models.PositiveIntegerField(default=0, verbose_name="Количество обновлений",
                                                help_text="Сколько раз была обновлена информация по фильтру")

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.slug = slugify(str(self)) + str(get_random_string(length=32))
        elif self.initialized:
            self.slug = f"{slugify(str(self))}{self.pk}"
        super().save(*args, **kwargs)
        # else:
        # self.slug = slugify(str(self)) + str(self.pk)
        # super().save(*args, **kwargs)

    def on_post_save(self):
        # TODO: check if there's a better way to add PK to the SLUG field
        if not self.initialized:
            self.slug = slugify(str(self)) + "-" + str(self.pk)
            self.initialized = True
            self.save()

    class Meta:
        abstract = True
        ordering = ['created_at']


class AbstractLocationModel(models.Model):
    slug = models.SlugField(unique=True, primary_key=True)
    name = models.CharField(max_length=60, unique=True)
    avito = models.CharField(max_length=60)
    autoru = models.CharField(max_length=60)
    drom = models.CharField(max_length=60)
    youla = models.CharField(max_length=60)
    popularCount = models.PositiveIntegerField(default=1)
    isPopular = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
        ordering = ['name']


# ---------------------------------------------------------------------------------------


class RegionDB(AbstractLocationModel):
    pass


class CityDB(AbstractLocationModel):
    region = models.ForeignKey(RegionDB, related_name='cities', on_delete=models.CASCADE, null=True)
    region_slug = models.CharField(max_length=100, default="")

    def save(self, *args, **kwargs):
        self.region_slug = self.region.slug
        super().save(*args, **kwargs)


class CarMark(AbstractOptionModel):
    name = models.CharField(max_length=60, unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class CarModel(AbstractOptionModel):
    name = models.CharField(max_length=60)
    parentMark = models.ForeignKey(CarMark, related_name='models', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.parentMark.name} {self.name}'

    def save(self, *args, **kwargs):
        self.slug = self.get_slug()
        super().save(*args, **kwargs)


class CarFilter(AbstractBaseFilterModel):
    owner = models.ForeignKey(Account, related_name='filters', on_delete=models.CASCADE)

    # carname_mark = models.CharField(max_length=30, verbose_name="Марка", blank=True)
    # carname_model = models.CharField(max_length=30, verbose_name="Модель", blank=True)
    regions = models.ManyToManyField('RegionDB', related_name="filters")
    cities = models.ManyToManyField('CityDB', related_name="filters")
    car_marks = models.ManyToManyField(CarMark, related_name="filters")
    car_models = models.ManyToManyField(CarModel, related_name="filters")
    hull = models.CharField(max_length=20, verbose_name="Кузов", blank=True)
    fuel = models.CharField(max_length=20, verbose_name="Тип двигателя", blank=True)
    transm = models.CharField(max_length=20, verbose_name="Трансмиссия", blank=True)
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


# class Location(models.Model):
#     filter = models.ForeignKey(CarFilter, related_name="locations", on_delete=models.CASCADE)
#     region = models.ForeignKey(RegionDB, related_name="locations", on_delete=models.CASCADE)
#     city = models.ForeignKey(CityDB, related_name="locations", on_delete=models.CASCADE)
#     use_city = models.BooleanField(default=False)
#
#     def save(self, *args, **kwargs):
#         if self.city is None:
#             self.use_city = False
#         else:
#             self.use_city = True
#         super().save(*args, **kwargs)
#
#
# class CarOption(models.Model):
#     filter = models.ForeignKey(CarFilter, related_name="locations", on_delete=models.CASCADE)
#     mark = models.ForeignKey(CarMark, related_name="car_options", on_delete=models.CASCADE)
#     model = models.ForeignKey(CarModel, related_name="car_options", on_delete=models.CASCADE)
#     use_model = models.BooleanField(default=False)
#
#     def save(self, *args, **kwargs):
#         if self.model is None:
#             self.use_model = False
#         else:
#             self.use_model = True


class CarElement(AbstractElementModel):
    """Модель результата поиска - автомобиль"""
    parentFilter = models.ForeignKey(CarFilter, related_name='cars', on_delete=models.CASCADE)
    year = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return f'{self.e_id} {self.parentFilter.owner.username} {self.pk}'


class OtherFilter(AbstractBaseFilterModel):
    find = models.CharField(max_length=100)
    owner = models.ForeignKey(Account, related_name='other_filters', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.owner} {self.find} {self.cities}'


class OtherElement(AbstractElementModel):
    parentFilter = models.ForeignKey(OtherFilter, related_name='cars', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.e_id} {self.parentFilter.owner.username} {self.pk}'
