from django.contrib.auth import user_logged_in
from rest_framework import viewsets, views, generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.compat import coreapi, coreschema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.schemas import ManualSchema
from rest_framework.views import APIView

from account.models import Account
from main.models import CarResult, CarFilter, CarMark, CarModel, City, Region
from .serializers import CarFilterSerializer, CarElementSerializer, CarMarkSerializer, CarModelSerializer, \
    RegionSerializer, CitySerializer, AccountSerializer, RegistrationSerializer, AccountPropertiesSerializer, \
    EmailAuthTokenSerializer


class UserFilters(generics.ListAPIView):
    serializer_class = CarFilterSerializer

    def get_queryset(self):
        user = self.request.user
        return CarFilter.objects.filter(owner=user)


class RegionsView(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    pagination_class = None
    filterset_fields = ['name']
    search_fields = ['name']


class CitiesView(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = (permissions.IsAuthenticated,)
    filterset_fields = ['name']
    search_fields = ['name']


class CarMarksView(viewsets.ModelViewSet):
    queryset = CarMark.objects.all()
    serializer_class = CarMarkSerializer
    permission_classes = (permissions.IsAuthenticated,)


class CarModelsView(viewsets.ModelViewSet):
    queryset = CarModel.objects.all()
    serializer_class = CarModelSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filterset_fields = ['name']
    search_fields = ['name']


class CarFiltersView(viewsets.ModelViewSet):
    queryset = CarFilter.objects.all()
    serializer_class = CarFilterSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filterset_fields = ['owner']

    def get_queryset(self):
        return CarFilter.objects.filter(owner=self.request.user)


class CarResultsView(viewsets.ModelViewSet):
    queryset = CarResult.objects.all()
    serializer_class = CarElementSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filterset_fields = ['e_id', 'year']
    search_fields = ['title']


class AccountView(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = None

    def get_queryset(self):
        return Account.objects.filter(pk=self.request.user.pk)


class GenAccountView(GenericAPIView):
    serializer_class = AccountSerializer
    pagination_class = None
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        serializer = AccountSerializer(instance=request.user)
        return Response(serializer.data)

    def get_queryset(self):
        return Account.objects.filter(pk=self.request.user.pk)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def registration_view(request):
    if request.method == 'POST':
        serializer = RegistrationSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            user = serializer.save()
            token, token_created = Token.objects.get_or_create(user=user)
            print(f'{token_created=}')
            data['userId'] = user.pk
            data['username'] = user.username
            data['email'] = user.email
            data['token'] = token.key
        else:
            data = serializer.errors
        return Response(data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_car_element_view(request, item_id):
    if request.method == 'GET':
        print(f'get_car_element_view called -- {item_id=}')
        data = {}
        try:
            car = CarResult.objects.get(id=item_id)
            serializer = CarElementSerializer(instance=car)
            data = serializer.data

        except CarResult.DoesNotExist as e:
            data['error'] = str(e)

        finally:
            return Response(data)


@api_view(['GET', 'PUT'])
@permission_classes([permissions.IsAuthenticated])
def account_properties_view(request):
    if request.method == 'GET':
        try:
            user = request.user
        except Account.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = AccountPropertiesSerializer(instance=user)
        return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def update_user_properties_view(request):
    if request.method == 'PUT':
        try:
            user = request.user
        except Account.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = AccountPropertiesSerializer(instance=user, data=request.data)
        data = {}
        if serializer.is_valid():
            serializer.save()
            data['response'] = "Account update success"
            return Response(data=data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):
    def get_object(self, pk):
        return Account.objects.get(pk=pk)

    def patch(self, request, pk):
        user = self.get_object(pk)
        serializer = AccountSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)


class ObtainAuthTokenByEmail(ObtainAuthToken):
    serializer_class = EmailAuthTokenSerializer
    if coreapi is not None and coreschema is not None:
        schema = ManualSchema(
            fields=[
                coreapi.Field(
                    name="email",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Email",
                        description="Valid email for authentication",
                    ),
                ),
                coreapi.Field(
                    name="password",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Password",
                        description="Valid password for authentication",
                    ),
                ),
            ],
            encoding="application/json",
        )

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        # token, created = Token.objects.get_or_create(user=user)
        user_logged_in.send(sender=user.__class__, request=request, user=user)
        return get_success_auth_response(user)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def auth_and_check_user(request):
    if request.method == 'GET':
        user_logged_in.send(sender=request.user.__class__, request=request, user=request.user)
        return get_success_auth_response(request.user)


# TODO: May move this somewhere else in the future
def get_success_auth_response(user):
    token, created = Token.objects.get_or_create(user=user)
    return Response({
        'userId': user.pk,
        'username': user.username,
        'email': user.email,
        'token': token.key
    })
