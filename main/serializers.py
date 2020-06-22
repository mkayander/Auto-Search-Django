from rest_framework import serializers

from .models import CarElement, CarFilter, CarMark, CarModel, CityDB, RegionDB, Account


class CarElementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CarElement
        fields = '__all__'


class CarFilterSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CarFilter
        fields = '__all__'


class CityDBSerializer(serializers.ModelSerializer):
    # region1 = serializers.HyperlinkedRelatedField(view_name='main:regiondb-detail', read_only=True, source='region')
    class Meta:
        model = CityDB
        fields = '__all__'


class RegionDBSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegionDB
        fields = '__all__'


class CarMarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarMark
        fields = '__all__'


class CarModelSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CarModel
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'
