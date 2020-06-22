from abc import ABC

from rest_framework import serializers
from rest_framework.authtoken.serializers import AuthTokenSerializer

from api.validators import is_email_address_valid
from main.models import CarElement, CarFilter, CarMark, CarModel, CityDB, RegionDB, Account


from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers


class EmailAuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField(label=_("Email"))
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if is_email_address_valid(email) and password:
            user = authenticate(request=self.context.get('request'),
                                username=email, password=password)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include correct "email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class RegionDBSerializer(serializers.ModelSerializer):
    # url = serializers.SlugRelatedField(
    #     many=True,
    #     read_only=True,
    #     slug_field='slug'
    # )
    class Meta:
        model = RegionDB
        fields = '__all__'
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class CityDBSerializer(serializers.ModelSerializer):
    # region = serializers.HyperlinkedRelatedField(many=True, view_name='main: regiondb-detail', read_only=True)
    # region = serializers.HyperlinkedIdentityField(view_name='regions-detail')
    # region = RegionDBSerializer()
    # region_slug = serializers.CharField(source="region.slug")

    class Meta:
        model = CityDB
        fields = '__all__'
        # fields = ('name', 'url', 'avitoCity', 'region')
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class CarMarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarMark
        fields = '__all__'


class CarModelSerializer(serializers.ModelSerializer):
    parentMark = serializers.CharField(source="parentMark.slug")

    class Meta:
        model = CarModel
        fields = '__all__'
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class CarFilterSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    # car_marks = CarMarkSerializer(read_only=True, many=True)
    # car_models = CarModelSerializer(read_only=True, many=True)
    # regions = RegionDBSerializer(read_only=True, many=True)
    # cities = CityDBSerializer(read_only=True, many=True)

    class Meta:
        model = CarFilter
        fields = '__all__'
        read_only_fields = ('owner', 'id', 'slug', 'fid', 'quantity', 'count')
        # lookup_field = 'id'
        # extra_kwargs = {
        #     'url': {'lookup_field': 'id'}
        # }


class CarElementSerializer(serializers.ModelSerializer):
    # parentFilter = serializers.RelatedField()
    pf_slug = serializers.CharField(source="parentFilter.slug")

    class Meta:
        model = CarElement
        fields = '__all__'
        # fields = ('url','e_id','title','car_url','slug','archived','site','year','price','created_at','parentFilter')
        # lookup_field = 'slug'
        # extra_kwargs = {
        #     'url': {'lookup_field': 'slug'}
        # }


class AccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = ["id",
                  # "password",
                  "email",
                  "username",
                  "date_joined",
                  "last_login",
                  "is_admin",
                  "is_active",
                  "is_staff",
                  "is_superuser"]


class RegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = Account
        fields = ['username', 'email', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def save(self, **kwargs):
        # super().save(**kwargs)
        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        if password != password2:
            raise serializers.ValidationError({'password': 'Passwords must match.'})

        user = Account(
            username=self.validated_data['username'],
            email=self.validated_data['email'],
            password=password
        )
        user.save()
        return user


# class ProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Profile
#         fields = ['id', 'image', 'is_verified', 'user']
#         read_only_fields = ['id', 'is_verified', 'user']


class AccountPropertiesSerializer(serializers.ModelSerializer):
    # profile = ProfileSerializer()
    # profile_id = serializers.PrimaryKeyRelatedField(source='profile', read_only=True)

    class Meta:
        model = Account
        fields = ['pk', 'email', 'username']
        # read_only_fields = ['pk']
