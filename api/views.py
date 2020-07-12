from django.contrib.auth import user_logged_in
from django.http import HttpRequest
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


# --- Generic DRF class-based model view sets -------------------------------

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
        """Show only user's filters."""
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
        """Show only user's account"""
        # TODO ModelViewSet might not be needed if it always returns just one result
        return Account.objects.filter(pk=self.request.user.pk)


# -------------------------------------------------------------


class UserFilters(generics.ListAPIView):
    """Shows search filters of the currently logged-in user."""
    serializer_class = CarFilterSerializer

    def get_queryset(self):
        user = self.request.user
        return CarFilter.objects.filter(owner=user)


class GenAccountView(GenericAPIView):
    """Shows serialized account data of the currently logged-in user."""
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
    """
    Register a new user using RegistrationSerializer.
    If request data is valid, save the user and return a success view with user data. Else, return serializer error.
    """
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
def get_car_result_by_id(request: HttpRequest, item_id: int):
    """API view to get car result serialized data by id (database PK)."""
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


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def account_properties_view(request):
    """Get account properties of the authenticated user."""
    if request.method == 'GET':
        try:
            user = request.user
        except Account.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = AccountPropertiesSerializer(instance=user)
        return Response(serializer.data)


class ObtainAuthTokenByEmail(ObtainAuthToken):
    """Login to system by acquiring auth token from email + password"""
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
        # Get serializer, if it validates request data, send "logged in" signal and return success view with user data
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        user_logged_in.send(sender=user.__class__, request=request, user=user)
        return get_success_auth_response(user)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def auth_and_check_user(request):
    """
    Send 'logged in' signal, return success view with user data.
    This is used for client to check if their token is valid and proceed. I.e: auto-auth upon app launch.
    """
    if request.method == 'GET':
        user_logged_in.send(sender=request.user.__class__, request=request, user=request.user)
        return get_success_auth_response(request.user)


# TODO: May move this somewhere else in the future
def get_success_auth_response(user):
    """Display some user info to indicate a successful authentication."""
    token, created = Token.objects.get_or_create(user=user)
    return Response({
        'userId': user.pk,
        'username': user.username,
        'email': user.email,
        'token': token.key
    })
