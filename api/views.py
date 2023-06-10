from rest_framework.filters import SearchFilter

from api.serializers import *
from rest_framework import generics
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from api.renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, logout
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from api.models import *
from rest_framework.permissions import IsAuthenticated
from django.db import connections
from django.db.models import Q

# Create your views here.

@api_view(['GET'])
def server_status(request):
    try:
        connections['default'].cursor()
        return Response({'status': 'ok'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'status': 'error', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


"""Controladores de user"""


class UserListCreate(generics.ListCreateAPIView):
    queryset = Users.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = UserSerializer
    # = (IsAuthenticated,)


class UsersDetail(generics.RetrieveUpdateAPIView):
    queryset = Users.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = UserSerializer
    #permission_classes = (IsAuthenticated,)


class UserProfileView(APIView):
    renderer_classes = [UserRenderer, ]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user  # Obtener el usuario autenticado

        serializer = ProfileUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'user_id': user.pk}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ValidateAccountView(APIView):
    def post(self, request, pk):
        token = request.data.get('token')
        user = get_object_or_404(Users, pk=pk)

        if default_token_generator.check_token(user, token):
            user.is_validated = True
            user.save()
            return Response({'detail': 'La cuenta ha sido validada exitosamente.'})

        return Response({'detail': 'El token de validación es inválido.'}, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    serializer_class = ChangePasswordSerializer
    #permission_classes = (IsAuthenticated,)

    def patch(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user: Users = request.user
        user.set_password(serializer.data.get('new_password'))
        user.save()
        return Response({'message': 'success'}, status=200)


class LoginView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        password = serializer.data.get('password')
        user = authenticate(email=email, password=password)
        if user is not None:
            token = get_tokens_for_user(user)
            return Response({'token': token, 'msg': 'Inicio de sesión exitoso'},
                            status=status.HTTP_200_OK)
        else:
            return Response({'errors': {'error_de_campo': ['Email o contraseña invalidos']}},
                            status=status.HTTP_404_NOT_FOUND)

class LogoutView(APIView):

    def post(self, request):
        logout(request)  # Cierra la sesión del usuario
        return Response({'msg': 'Se cerro la sesión con éxito'},
                        status=status.HTTP_200_OK)  # Retorna un mensaje de éxito en la respuesta

class SendPasswordResetEmailView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = SendPasswordResetEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'msg': 'Link para reiniciar contraseña enviado'}, status=status.HTTP_200_OK)


class UserPasswordResetView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, uid, token, format=None):
        serializer = UserPasswordResetSerializer(data=request.data, context={'uid': uid, 'token': token})
        serializer.is_valid(raise_exception=True)
        return Response({'msg': 'Cambio de contraseña exitoso'}, status=status.HTTP_200_OK)


"""Demas controladores"""


class ShopListCreate(generics.ListCreateAPIView):
    queryset = Shop.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = ShopSerializer
    #permission_classes = (IsAuthenticated,)


class ShopDetail(generics.RetrieveUpdateAPIView):
    queryset = Shop.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = ShopSerializer
    #permission_classes = (IsAuthenticated,)


class ReportSettingList(generics.ListAPIView):
    queryset = ReportSettings.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = ReportSettingsSerializer
    #permission_classes = (IsAuthenticated,)


class ReportSettingDetail(generics.RetrieveUpdateAPIView):
    queryset = ReportSettings.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = ReportSettingsSerializer
    #permission_classes = (IsAuthenticated,)


class RecommendationsList(generics.ListAPIView):
    queryset = Recommendations.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = RecommendationsSerializer
    #permission_classes = (IsAuthenticated,)


class RecommendationsDetail(generics.RetrieveUpdateAPIView):
    queryset = Recommendations.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = RecommendationsSerializer
    #permission_classes = (IsAuthenticated,)


class NotificationList(generics.ListAPIView):
    queryset = Notification.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = NotificationSerializer
    #permission_classes = (IsAuthenticated,)


class NotificationDetail(generics.RetrieveUpdateAPIView):
    queryset = Notification.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = NotificationSerializer
    #permission_classes = (IsAuthenticated,)


class UserNotificationDetail(generics.RetrieveUpdateAPIView):
    queryset = UserNotification.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = UserNotificationSerializer
    #permission_classes = (IsAuthenticated,)


class FinancesListCreate(generics.ListCreateAPIView):
    queryset = Finance.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = FinanceSerializer
    #permission_classes = (IsAuthenticated,)


class FinancesDetail(generics.RetrieveUpdateAPIView):
    queryset = Finance.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = FinanceSerializer
    #permission_classes = (IsAuthenticated,)


# Vista para listar y crear finanzas de usuario.
class UserFinancesListCreate(generics.ListCreateAPIView):
    queryset = UserFinances.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = UserFinancesSerializer
    filter_backends = [SearchFilter]
    search_fields = ['type', 'total']
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = super().get_queryset()
        #Obtiene los parametros de busqueda de la URL
        finance_type = self.request.query_params.get('finance_type', None)
        total_min = self.request.query_params.get('total_min', None)
        total_max = self.request.query_params.get('total_max', None)
        if finance_type:
            queryset = queryset.filter(type=finance_type)#Filtra las finanzas por tipo.
        if total_min:
            queryset = queryset.filter(total__gte=total_min) #Filtra las finanzas por un valor minimo de total.
        if total_max:
            queryset = queryset.filter(total__lte=total_max)#Filtra las finanzas por un valor maximo de total.
        return queryset


class UserFinancesDetail(generics.RetrieveUpdateAPIView):
    queryset = UserFinances.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = UserFinancesSerializer
    #permission_classes = (IsAuthenticated,)


class SupplierListCreate(generics.ListCreateAPIView):
    queryset = Supplier.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = SupplierSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name']
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        return queryset


class SupplierDetail(generics.RetrieveUpdateAPIView):
    queryset = Supplier.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = SupplierSerializer
    #permission_classes = (IsAuthenticated,)


class DebtorListCreate(generics.ListCreateAPIView):
    queryset = Debtor.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = DebtorSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name']
    #permission_classes = (IsAuthenticated,)


class DebtorDetail(generics.RetrieveUpdateAPIView):
    queryset = Debtor.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = DebtorSerializer
    #permission_classes = (IsAuthenticated,)


# View para listar y crear categorías.
class CategoryListCreate(generics.ListCreateAPIView):
    queryset = Category.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = CategorySerializer
    #permission_classes = (IsAuthenticated,)


# View para obtener detalles y actualizar una categoría específica.
class CategoryDetail(generics.RetrieveUpdateAPIView):
    queryset = Category.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = CategorySerializer
    #permission_classes = (IsAuthenticated,)


# View para listar y crear ítems.
class ItemListCreate(generics.ListCreateAPIView):
    queryset = Item.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = ItemSerializer
    filter_backends = [SearchFilter] #filtros backend para el nombre precio de compra y precio de venta
    search_fields = ['name', 'buy_price', 'sell_price']
    #permission_classes = (IsAuthenticated,)


# View para obtener detalles y actualizar un ítem específico.
class ItemDetail(generics.RetrieveUpdateAPIView):
    queryset = Item.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = ItemSerializer
    #permission_classes = (IsAuthenticated,)


# View para listar y crear ítems de tienda.
class ShopItemsListCreate(generics.ListCreateAPIView):
    queryset = ShopItems.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = ShopItemsSerializer
    #permission_classes = (IsAuthenticated,)


# View para obtener detalles y actualizar un ítem de tienda específico.
class ShopItemsDetail(generics.RetrieveUpdateAPIView):
    queryset = ShopItems.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = ShopItemsSerializer
    #permission_classes = (IsAuthenticated,)


# View para listar y crear ítems de deudor de usuario.
class UserDebtorItemsListCreate(generics.ListCreateAPIView):
    queryset = UserDebtorItems.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = UserDebtorItemsSerializer
    #permission_classes = (IsAuthenticated,)


# View para obtener detalles y actualizar un ítem de deudor de usuario específico.
class UserDebtorItemsDetail(generics.RetrieveUpdateAPIView):
    queryset = UserDebtorItems.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = UserDebtorItemsSerializer
    #permission_classes = (IsAuthenticated,)


# View para eliminado logico.
class SupplierRemoveListView(generics.RetrieveUpdateAPIView):
    queryset = Supplier.objects.filter(is_deleted=False)
    serializer_class = RemoveSupplierSerializer
    # permission_classes = (IsAuthenticated,)


# View para eliminado logico.
class RemoveUserFinanceView(generics.RetrieveUpdateAPIView):
    queryset = UserFinances.objects.filter(is_deleted=False)
    serializer_class = RemoveUserFinanceSerializer
    #permission_classes = (IsAuthenticated,)


# View para listar tiendas con capacidad de búsqueda.
class ShopListView(generics.ListAPIView):
    serializer_class = ShopListSerializer
    #permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = Shop.objects.filter(is_deleted=False) #Obtiene todas las tiendas que no han sido eliminadas.
        search_query = self.request.query_params.get('search', None)#Obtiene el parametro de busqueda de la URL.
        if search_query:
            # Filtra las tiendas por nombre o dirección que coincidan con el criterio de busqueda.
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(address__icontains=search_query)
            )

        return queryset


# View para obtener detalles de una tienda específica.
class ShopDetailView(generics.RetrieveAPIView):
    queryset = Shop.objects.filter(is_deleted=False)
    serializer_class = ShopProfileSerializer
    #permission_classes = (IsAuthenticated,)

# View para eliminado logico.
class RemoveItemView(generics.RetrieveUpdateAPIView):
    queryset = Item.objects.filter(is_deleted=False)
    serializer_class = RemoveItemSerializer
    #permission_classes = (IsAuthenticated,)


#view para vender productos
class SellItemView(generics.UpdateAPIView):
    queryset = Item.objects.filter(is_deleted=False)
    serializer_class = SellItemSerializer
    # permission_classes = (IsAuthenticated,)


#view para vender a fiados
class UserDebtorItemsCreateView(generics.ListCreateAPIView):
    serializer_class = SellDebtorItemSerializer
    # permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = UserDebtorItems.objects.filter(is_deleted=False)
        search_query = self.request.query_params.get('search', None)# Obtiene el parámetro de busqueda que le llega a la peticion
        if search_query:
            queryset = queryset.filter(items_id__name__icontains=search_query)# Filtra los registros por el nombre del producto
        return queryset


class RemoveUserDebtorItemsView(generics.RetrieveUpdateAPIView):
    queryset = UserDebtorItems.objects.filter(is_deleted=False)
    serializer_class = RemoveUserDebtorItemsSerializer
    #permission_classes = (IsAuthenticated,)


class RemoveDebtorView(generics.RetrieveUpdateAPIView):
    queryset = Debtor.objects.filter(is_deleted=False)
    serializer_class = RemoveDebtorSerializer
    #permission_classes = (IsAuthenticated,)